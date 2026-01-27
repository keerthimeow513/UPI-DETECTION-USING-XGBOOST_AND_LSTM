from pydantic import BaseModel # Import BaseModel from Pydantic to enable automatic data validation and JSON parsing
from typing import Optional # Import Optional for fields that are allowed to be null or missing

class TransactionRequest(BaseModel): # Define the expected data structure for an incoming payment request
    SenderUPI: str # The unique UPI ID of the person sending money (e.g., 'user@bank')
    ReceiverUPI: str # The unique UPI ID of the person or merchant receiving money
    Amount: float # The monetary value of the transaction in decimal format
    DeviceID: str # The hardware MAC address or unique identifier of the mobile device being used
    Latitude: float # The GPS latitude coordinate of the device at the time of payment
    Longitude: float # The GPS longitude coordinate of the device at the time of payment
    # The timestamp is optional because the server can generate it if the app doesn't provide one
    Timestamp: Optional[str] = None 

class PredictionResponse(BaseModel): # Define the data structure that the API will return back to the user
    transaction_id: str # A unique tracking ID for this specific prediction request
    risk_score: float # The calculated probability of fraud ranging from 0.0 (Safe) to 1.0 (Certain Fraud)
    verdict: str  # The final recommendation: "BLOCK" (Fraud), "FLAG" (Suspected), or "ALLOW" (Safe)
    factors: dict # A dictionary containing the top reasons/features that contributed to the score (SHAP values)
