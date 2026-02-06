"""
UPI Fraud Detection API - FastAPI Application

This module provides the REST API interface for the fraud detection system.
It handles HTTP requests, CORS configuration, and orchestrates the prediction pipeline.

Example:
    Run the server:
        $ uvicorn 04_inference.api:app --reload
    
    Or directly:
        $ python 04_inference/api.py

Endpoints:
    GET  /         - Health check
    POST /predict  - Fraud detection prediction
"""

import sys
import os
from contextlib import asynccontextmanager

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid

from schemas import TransactionRequest, PredictionResponse
from service import FraudDetectionService


# Global service instance
service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    This replaces the deprecated @app.on_event("startup") decorator
    and provides better cross-platform compatibility (especially Windows).
    
    Yields:
        None: After loading models, allowing the app to run.
    """
    # Startup: Load models
    global service
    config_path = os.path.join(project_root, '07_configs', 'config.yaml')
    service = FraudDetectionService(config_path)
    yield
    # Shutdown: Cleanup if needed
    pass


# Initialize FastAPI with lifespan
app = FastAPI(
    title="UPI Fraud Detection API",
    description="Real-time hybrid AI scoring engine for UPI transactions",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status and system name
        
    Example:
        GET /
        Response: {"status": "online", "system": "UPI Fraud Shield"}
    """
    return {"status": "online", "system": "UPI Fraud Shield"}


@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(txn: TransactionRequest):
    """
    Fraud detection prediction endpoint.
    
    Analyzes a transaction and returns risk score, verdict, and factors.
    
    Args:
        txn (TransactionRequest): Transaction details including:
            - SenderUPI, ReceiverUPI
            - Amount
            - DeviceID
            - Latitude, Longitude
            - Hour, DayOfWeek, DayOfMonth
            - TimeDiff, AmountDiff
    
    Returns:
        PredictionResponse: Contains:
            - transaction_id (str): Unique ID for the request
            - risk_score (float): Fraud probability (0-1)
            - verdict (str): ALLOW, FLAG, or BLOCK
            - factors (dict): Top risk factors from SHAP analysis
    
    Raises:
        HTTPException: 500 if prediction fails
        
    Example:
        POST /predict
        {
            "SenderUPI": "user@upi",
            "ReceiverUPI": "shop@upi",
            "Amount": 500.0,
            "DeviceID": "device123",
            "Latitude": 12.97,
            "Longitude": 77.59,
            "Hour": 14
        }
    """
    try:
        txn_id = str(uuid.uuid4())
        data = txn.model_dump()
        result = service.predict(data)
        
        return {
            "transaction_id": txn_id,
            "risk_score": result['risk_score'],
            "verdict": result['verdict'],
            "factors": result['factors']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
