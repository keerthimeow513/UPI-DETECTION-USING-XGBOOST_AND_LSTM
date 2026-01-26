from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import sys
import os

# Add project root
sys.path.append(os.getcwd())

from inference.schemas import TransactionRequest, PredictionResponse
from inference.service import FraudDetectionService

app = FastAPI(
    title="UPI Fraud Detection API",
    description="Real-time hybrid AI scoring engine for UPI transactions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Service
service = None

@app.on_event("startup")
def load_artifacts():
    global service
    service = FraudDetectionService()

@app.get("/")
def health_check():
    return {"status": "online", "system": "UPI Fraud Shield"}

@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(txn: TransactionRequest):
    try:
        # Generate a transaction ID if one isn't real (Integration Simulation)
        txn_id = str(uuid.uuid4())
        
        # Convert Pydantic model to dict
        data = txn.dict()
        
        # Run inference
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
