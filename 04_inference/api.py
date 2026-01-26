import sys
import os

# 1. Add the current directory (04_inference) to sys.path
# This allows 'import schemas' and 'import service' to work directly
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. Add the project root to sys.path
# This allows 'import utils' to work (assuming utils is in root)
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid

# Import local modules directly now that path is set
from schemas import TransactionRequest, PredictionResponse
from service import FraudDetectionService

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
    # Config path relative to project root
    config_path = os.path.join(project_root, '07_configs', 'config.yaml')
    service = FraudDetectionService(config_path)

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
