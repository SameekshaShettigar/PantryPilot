from fastapi import FastAPI

app = FastAPI(title="PantryPilot API")


@app.get("/health")
def health_check():
    return {"status": "healthy"}