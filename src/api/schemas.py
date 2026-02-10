# Pydantic Models
# This module contains all Pydantic models for request/response schemas

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TransactionRequest(BaseModel):
    """Request model for fraud prediction"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    sender_id: str = Field(..., description="Sender's UPI ID")
    receiver_id: str = Field(..., description="Receiver's UPI ID")
    amount: float = Field(..., gt=0, description="Transaction amount")
    transaction_type: str = Field(..., description="Type of transaction")
    merchant_category: Optional[str] = Field(None, description="Merchant category code")
    device_id: Optional[str] = Field(None, description="Device identifier")
    location: Optional[str] = Field(None, description="Transaction location")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")


class FraudPredictionResponse(BaseModel):
    """Response model for fraud prediction"""
    transaction_id: str
    is_fraud: bool
    fraud_probability: float
    risk_score: int
    confidence: float
    features_analyzed: int
    prediction_time_ms: float
    timestamp: datetime


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    timestamp: datetime
    model_loaded: bool
    database_connected: bool


class TokenRequest(BaseModel):
    """Request model for authentication token"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication token"""
    access_token: str
    token_type: str
    expires_in: int
