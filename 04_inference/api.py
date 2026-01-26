import sys
import os

# Add project root to path (must be BEFORE imports that rely on it)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid

# Correct imports: Since we are inside the package, or running as script
# We'll use relative imports if run as module, or absolute if path added.
# Given sys.path adjustment, we can import from the module name if '04_inference' is a package,
# OR we can import relatively if we run correctly.
# Simplest fix for "python api.py" or "uvicorn api:app" inside the folder:
try:
    from schemas import TransactionRequest, PredictionResponse
    from service import FraudDetectionService
except ImportError:
    from 04_inference.schemas import TransactionRequest, PredictionResponse
    from 04_inference.service import FraudDetectionService

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
    service = FraudDetectionService('07_configs/config.yaml')

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
