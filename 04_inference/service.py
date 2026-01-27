import sys # Import system-specific parameters and functions
import os # Import operating system interfaces for file path management

# Add project root to path so we can import from 'utils' even if we run this script from inside the '04_inference' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable GPU completely for TensorFlow to ensure stability and avoid library conflicts in production/CPU environments
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf # Import TensorFlow for running the deep learning LSTM model
import xgboost as xgb # Import XGBoost for running the gradient boosting tree model
import joblib # Import joblib for loading serialized model files (.pkl)
import numpy as np # Import numpy for matrix and array operations
import yaml # Import yaml for reading the configuration file
import shap # Import SHAP (SHapley Additive Explanations) for model transparency/explainability
from utils.preprocessing import Preprocessor # Import our custom data transformation class
from utils.logger import setup_logger # Import our custom logging utility

logger = setup_logger() # Initialize the logger for this service

class FraudDetectionService: # Define the main service class that orchestrates fraud prediction
    def __init__(self, config_path="07_configs/config.yaml"): # Initialize the service with the path to the config file
        with open(config_path, 'r') as f: # Open the config file in read mode
            self.config = yaml.safe_load(f) # Load configuration parameters into a dictionary
            
        self.preprocessor = Preprocessor(config_path) # Initialize the preprocessor instance
        self.load_models() # Call the internal method to load AI models into memory
        
    def load_models(self): # Method to load all trained AI models and supporting artifacts
        logger.info("Loading models for inference...") # Log that the model loading process has started
        path = self.config['paths']['artifacts'] # Get the directory path where models are stored
        self.lstm_model = tf.keras.models.load_model(os.path.join(path, 'lstm_model.h5')) # Load the saved Keras/TensorFlow LSTM model
        self.xgb_model = joblib.load(os.path.join(path, 'xgb_model.pkl')) # Load the saved XGBoost classifier
        self.preprocessor.load_artifacts() # Load the fitted scalers and encoders via the preprocessor
        
        # Initialize SHAP explainer specifically for the XGBoost model to provide factor analysis
        # Note: TreeExplainer is highly optimized for tree-based models like XGBoost
        self.explainer = shap.TreeExplainer(self.xgb_model)
        
    def predict(self, transaction_data: dict): # Main method to perform an end-to-end fraud risk assessment
        """
        End-to-end prediction pipeline
        """
        # 1. Preprocess the incoming raw dictionary into a numerical vector
        # Note: LSTM needs a sequence (3D input). In this demo API, we mock history by padding.
        # In production, we would query a Feature Store (Redis) to get the user's real last 10 txns.
        
        feature_vector = self.preprocessor.transform_single(transaction_data) # Convert raw fields to normalized numbers
        
        # Prepare inputs for the XGBoost model (Needs 2D: [1, n_features])
        xgb_input = feature_vector.reshape(1, -1)
        
        # Prepare inputs for the LSTM model (Needs 3D: [1, sequence_length, n_features])
        # We use np.tile to duplicate the current feature vector to simulate a stable recent history
        lstm_input = np.tile(feature_vector, (1, self.config['data']['lookback'], 1))
        
        # 2. Run Inference through both models
        lstm_score = float(self.lstm_model.predict(lstm_input, verbose=0)[0][0]) # Get LSTM risk probability (0 to 1)
        xgb_score = float(self.xgb_model.predict_proba(xgb_input)[0][1]) # Get XGBoost risk probability (0 to 1)
        
        # 3. Hybrid Logic (Average the AI scores)
        final_score = 0.5 * lstm_score + 0.5 * xgb_score
        
        # 4. Explainability (Calculate SHAP values for the current transaction)
        shap_values = self.explainer.shap_values(xgb_input) # Determine how much each feature added/removed from risk
        feature_names = self.preprocessor.feature_names # Get the names of the features in order
        factors = dict(zip(feature_names, shap_values[0].tolist())) # Map values back to their readable feature names
        
        # Sort factors by their absolute impact to find the top 5 most important reasons
        sorted_factors = dict(sorted(factors.items(), key=lambda item: abs(item[1]), reverse=True)[:5])

        # --- DOMAIN RULE ENHANCEMENT (Hybrid Safety Layer) ---
        # AI models sometimes miss "Account Takeover" if the transaction looks normal otherwise.
        # We apply a context-aware rule for unknown devices and suspicious patterns.
        
        KNOWN_SAFE_DEVICE = "82:4e:8e:2a:9e:28" # Mock registered device for the test user
        input_device = transaction_data.get("DeviceID", "") # Get the device ID from the input
        amount = transaction_data.get("Amount", 0) # Get the transaction amount
        hour = transaction_data.get("Hour", 12) # Get the hour of transaction
        
        # Rule 1: Unknown Device Check
        if input_device != KNOWN_SAFE_DEVICE: # If the device doesn't match the user's registered hardware...
            logger.warning(f"Domain Rule Triggered: Unknown Device {input_device}") # Log the anomaly
            
            # Context-Aware Decision for Unknown Device:
            # 1. If it is an unknown device AND (high amount OR AI is suspicious), we BLOCK (Score 0.95).
            if final_score > 0.4 or amount > 10000:
                final_score = max(final_score, 0.95)
                sorted_factors["Unknown Device + High Risk"] = 0.50
            else:
                # 2. If it is an unknown device but behavior looks normal, we FLAG (Score 0.6) for OTP.
                final_score = max(final_score, 0.6)
                sorted_factors["New Device (OTP Required)"] = 0.30
        
        # Rule 2: Unusual Hour + High Amount Check (Even for Safe Device)
        elif amount > 10000 and (hour < 5 or hour > 23):
            logger.warning(f"Domain Rule Triggered: High Amount at Unusual Hour")
            final_score = max(final_score, 0.6) # FLAG for OTP
            sorted_factors["Unusual Hour + High Amount"] = 0.40
            
        # 5. Determine the Verdict based on the final risk score
        verdict = "ALLOW" # Default action: Let the transaction through
        if final_score > 0.8: # If risk is very high...
            verdict = "BLOCK" # Hard block the transaction
        elif final_score > 0.5: # If risk is medium...
            verdict = "FLAG" # Flag for manual verification or OTP challenge
            
        return { # Return the comprehensive results dictionary
            "risk_score": final_score, # The combined 0-1 risk probability
            "verdict": verdict, # The final decision (ALLOW/FLAG/BLOCK)
            "lstm_score": lstm_score, # Raw probability from the deep learning model
            "xgb_score": xgb_score, # Raw probability from the tree-based model
            "factors": sorted_factors # Top 5 reasons behind the decision
        }
