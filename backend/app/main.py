from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.images import router as image_router
from app.api.pantry import router as pantry_router
from app.api.recipes import router as recipe_router
from app.api.shopping_list import router as shopping_list_router
from app.db.database import Base, engine


app = FastAPI(title="PantryPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(pantry_router)
app.include_router(image_router)
app.include_router(recipe_router)
app.include_router(shopping_list_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}