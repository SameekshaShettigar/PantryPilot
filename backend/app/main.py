from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.user import User

from app.models.pantry_item import PantryItem
from app.api.pantry import router as pantry_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PantryPilot API")
app.include_router(pantry_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}