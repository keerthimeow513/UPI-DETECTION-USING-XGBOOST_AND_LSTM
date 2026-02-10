# Prediction Routes
# This module contains the /predict endpoint

from fastapi import APIRouter, HTTPException
from src.api.schemas import TransactionRequest, FraudPredictionResponse
from src.services.fraud_detection import fraud_detection_service
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=FraudPredictionResponse)
async def predict_fraud(request: TransactionRequest):
    """
    Predict if a transaction is fraudulent
    
    Args:
        request: Transaction details
        
    Returns:
        Fraud prediction with probability and risk score
    """
    try:
        result = await fraud_detection_service.predict(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch")
async def batch_predict():
    """Batch prediction endpoint"""
    # TODO: Implement batch prediction
    return {"message": "Batch prediction not implemented yet"}
