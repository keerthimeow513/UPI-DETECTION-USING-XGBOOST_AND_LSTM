import sys # Import system library for path manipulation
import os # Import OS library for file and directory operations

# 1. Add the current directory (04_inference) to sys.path
# This ensures that when we call 'import schemas', Python looks in this folder first
current_dir = os.path.dirname(os.path.abspath(__file__)) # Get the absolute path of the directory where this file resides
sys.path.append(current_dir) # Add it to the Python module search path

# 2. Add the project root to sys.path
# This allows the API to reach out and import the 'utils' package from the root directory
project_root = os.path.abspath(os.path.join(current_dir, '..')) # Calculate the parent directory (project root)
sys.path.append(project_root) # Add the root directory to the Python module search path

from fastapi import FastAPI, HTTPException # Import FastAPI for building the web server and HTTPException for error responses
from fastapi.middleware.cors import CORSMiddleware # Import CORS middleware to allow the API to be called from different domains (like a frontend)
import uvicorn # Import Uvicorn, a lightning-fast ASGI server to run the FastAPI app
import uuid # Import UUID to generate unique transaction IDs for every request

# Import our custom local modules for data validation and core AI logic
from schemas import TransactionRequest, PredictionResponse # Import Pydantic models for request/response validation
from service import FraudDetectionService # Import the brain of the system: the detection service

app = FastAPI( # Initialize the FastAPI application instance
    title="UPI Fraud Detection API", # Set the title shown in the auto-generated /docs
    description="Real-time hybrid AI scoring engine for UPI transactions", # Set the description for the API
    version="1.0.0" # Set the API version
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware( # Add a security layer to manage incoming web requests
    CORSMiddleware,
    allow_origins=["*"], # Allow any website to call this API (useful for development)
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all HTTP headers
)

# Initialize a global service variable; it will hold our loaded models
service = None

@app.on_event("startup") # Define a hook that runs automatically when the server starts up
def load_artifacts(): # Function to load AI models into memory once, rather than on every request
    global service # Access the global service variable
    # Calculate the absolute path to the config file relative to the project root
    config_path = os.path.join(project_root, '07_configs', 'config.yaml') 
    service = FraudDetectionService(config_path) # Instantiate the service, which loads the LSTM and XGBoost models

@app.get("/") # Define a basic "GET" endpoint at the root URL
def health_check(): # Function to check if the API is alive
    return {"status": "online", "system": "UPI Fraud Shield"} # Return a simple JSON status

@app.post("/predict", response_model=PredictionResponse) # Define the main endpoint for fraud analysis via "POST"
def predict_fraud(txn: TransactionRequest): # Function that accepts a validated TransactionRequest JSON object
    try: # Start error handling to catch and report server-side issues
        # Generate a new unique transaction ID if one isn't provided by the calling system
        txn_id = str(uuid.uuid4())
        
        # Convert the Pydantic data model into a standard Python dictionary for the AI service
        data = txn.model_dump()
        
        # Pass the dictionary to our AI brain (the service) to get the risk score and verdict
        result = service.predict(data)
        
        return { # Construct and return the final JSON response to the client
            "transaction_id": txn_id, # The unique ID for this request
            "risk_score": result['risk_score'], # The calculated fraud probability (0 to 1)
            "verdict": result['verdict'], # The final decision: BLOCK, FLAG, or ALLOW
            "factors": result['factors'] # The top reasons behind the score (from SHAP)
        }
        
    except Exception as e: # Catch any errors that occur during processing (e.g., model failure)
        raise HTTPException(status_code=500, detail=str(e)) # Return a 500 error code with the error details

if __name__ == "__main__": # Entry point for running the script directly via 'python api.py'
    # Start the web server on all network interfaces (0.0.0.0) at port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
