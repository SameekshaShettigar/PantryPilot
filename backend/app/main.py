from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PantryPilot API")


@app.get("/health")
def health_check():
    return {"status": "healthy"}