from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import recommendation, analytics
from app.config import settings
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered skincare recommendation system that analyzes facial images",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp images directory and serve static files
temp_dir = "temp_images"
os.makedirs(temp_dir, exist_ok=True)
app.mount("/temp_images", StaticFiles(directory=temp_dir), name="temp_images")

# Include routers
app.include_router(
    recommendation.router,
    prefix="/api/v1/recommendations",
    tags=["recommendations"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Skincare Recommendation API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_provider": settings.primary_llm_provider
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)