# Health Routes
# This module contains the /health endpoints

from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.services.fraud_detection import fraud_detection_service
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        API health status and component states
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow(),
        "model_loaded": fraud_detection_service.is_model_loaded(),
        "database_connected": True  # TODO: Check actual database connection
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe endpoint
    
    Returns:
        API readiness status
    """
    if fraud_detection_service.is_model_loaded():
        return {"status": "ready"}
    return {"status": "not_ready", "reason": "Model not loaded"}


@router.get("/live")
async def liveness_check():
    """
    Liveness probe endpoint
    
    Returns:
        API liveness status
    """
    return {"status": "alive"}
