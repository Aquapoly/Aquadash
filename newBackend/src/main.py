from fastapi import FastAPI
from src.api.v1.api_router import api_router

app = FastAPI(title="Aquadash API")

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return {"status": "ok", "message": "Aquadash API is running."}

# Include the main API router with a prefix
app.include_router(api_router, prefix="/api/v1")
