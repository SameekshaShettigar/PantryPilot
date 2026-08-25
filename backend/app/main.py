import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import router as agent_router
from app.api.auth import router as auth_router
from app.api.images import router as image_router
from app.api.notifications import router as notifications_router
from app.api.pantry import router as pantry_router
from app.api.recipes import router as recipe_router
from app.api.shopping_list import router as shopping_list_router
from app.api.websockets import router as websockets_router
from app.db.database import Base, engine
from app.services.websocket_manager import manager, redis_pubsub_listener

# Ensure all database models are registered with Base metadata
import app.models.user
import app.models.pantry_item
import app.models.notification
import app.models.recipe
import app.models.shopping_list
import app.models.image


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create all database tables on application startup
    Base.metadata.create_all(bind=engine)
    
    # Start Redis Pub/Sub listener background task
    listener_task = asyncio.create_task(redis_pubsub_listener(manager))
    yield
    # Cancel listener task on shutdown
    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="PantryPilot API", lifespan=lifespan)

# CORS configuration: Explicit origins required when allow_credentials=True according to W3C CORS spec
origins = [
    "https://pantry-pilot-rosy-six.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(pantry_router)
app.include_router(image_router)
app.include_router(recipe_router)
app.include_router(shopping_list_router)
app.include_router(notifications_router)
app.include_router(agent_router)
app.include_router(websockets_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}