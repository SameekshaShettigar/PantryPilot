from datetime import date, datetime, timedelta
import logging
from celery import Celery

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.notification import Notification
from app.models.pantry_item import PantryItem

logger = logging.getLogger("pantrypilot.worker")

# Initialize Celery app
celery_app = Celery(
    "pantrypilot_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-expiring-pantry-items-hourly": {
            "task": "app.worker.check_expiring_items",
            "schedule": 3600.0,  # Run every hour
        },
    },
)


@celery_app.task(name="app.worker.check_expiring_items")
def check_expiring_items():
    """
    Celery Background Task:
    1. Periodically queries PostgreSQL for pantry items expiring in <= 3 days.
    2. Enforces idempotency (duplicate prevention) to avoid spamming the user.
    3. Creates persistent Notification records in PostgreSQL.
    """
    db = SessionLocal()
    notifications_created = 0

    try:
        today = date.today()
        expiry_threshold = today + timedelta(days=3)

        # Query all pantry items with an expiry date <= today + 3 days
        expiring_pantry_items = (
            db.query(PantryItem)
            .filter(
                PantryItem.expiry_date.isnot(None),
                PantryItem.expiry_date <= expiry_threshold,
            )
            .all()
        )

        for item in expiring_pantry_items:
            days_remaining = (item.expiry_date - today).days

            # -------------------------------------------------------------
            # Idempotency / Duplicate Prevention Rule:
            # Check if an unread notification for (user_id, pantry_item_id)
            # already exists OR if a notification was created today.
            # -------------------------------------------------------------
            start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            existing_notification = (
                db.query(Notification)
                .filter(
                    Notification.user_id == item.user_id,
                    Notification.pantry_item_id == item.id,
                    (Notification.is_read == False) | (Notification.created_at >= start_of_today),
                )
                .first()
            )

            if existing_notification:
                # Duplicate notification prevented!
                continue

            # Determine severity and message
            if days_remaining <= 0:
                msg = f"⚠️ CRITICAL: {item.name} has expired ({item.expiry_date})!"
                n_type = "critical"
            elif days_remaining == 1:
                msg = f"⚠️ URGENT: {item.name} expires tomorrow ({item.expiry_date})!"
                n_type = "urgent"
            else:
                msg = f"🔔 WARNING: {item.name} expires in {days_remaining} days ({item.expiry_date})."
                n_type = "warning"

            new_notification = Notification(
                user_id=item.user_id,
                pantry_item_id=item.id,
                message=msg,
                notification_type=n_type,
                is_read=False,
            )

            db.add(new_notification)
            notifications_created += 1

        db.commit()
        print(f"[CELERY WORKER] check_expiring_items executed. Created {notifications_created} new notification(s).")
        logger.info(f"[CELERY WORKER] check_expiring_items executed. Created {notifications_created} new notification(s).")
        return {"status": "success", "notifications_created": notifications_created}

    except Exception as exc:
        db.rollback()
        print(f"[CELERY WORKER ERROR] Failed to check expiring items: {exc}")
        logger.error(f"[CELERY WORKER ERROR] Failed to check expiring items: {exc}")
        raise exc
    finally:
        db.close()
