from pydantic import BaseModel
from typing import Optional

class TransactionRequest(BaseModel):
    SenderUPI: str
    ReceiverUPI: str
    Amount: float
    DeviceID: str
    Latitude: float
    Longitude: float
    # In a real integration, the system would fetch history. 
    # Here we might accept them or mock them.
    Timestamp: Optional[str] = None 

class PredictionResponse(BaseModel):
    transaction_id: str
    risk_score: float
    verdict: str  # "BLOCK", "FLAG", "ALLOW"
    factors: dict # SHAP values or reasons
