from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class TransactionRequest(BaseModel):
    SenderUPI: str = Field(..., min_length=3, max_length=100, description="Sender UPI ID")
    ReceiverUPI: str = Field(..., min_length=3, max_length=100, description="Receiver UPI ID")
    Amount: float = Field(..., ge=0, le=10000000, description="Transaction amount in INR")
    DeviceID: str = Field(..., min_length=1, max_length=100, description="Device identifier")
    Latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    Longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    Timestamp: Optional[str] = Field(None, description="Transaction timestamp (ISO format)")
    
    @field_validator('SenderUPI', 'ReceiverUPI')
    @classmethod
    def validate_upi(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('UPI ID must contain @ symbol (e.g., user@upi)')
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$', v):
            raise ValueError('UPI ID format invalid')
        return v
    
    @field_validator('Amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 10000000:
            raise ValueError('Amount cannot exceed 1 crore (10,000,000)')
        return v

class PredictionResponse(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    risk_score: float = Field(..., ge=0, le=1, description="Fraud probability (0-1)")
    verdict: str = Field(..., pattern="^(ALLOW|FLAG|BLOCK)$", description="Final decision")
    factors: dict = Field(..., description="Risk factors from SHAP analysis")
