import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable GPU completely for TensorFlow
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf
import xgboost as xgb
import joblib
import numpy as np
import yaml
import shap
from utils.preprocessing import Preprocessor
from utils.logger import setup_logger

logger = setup_logger()

class FraudDetectionService:
    def __init__(self, config_path="07_configs/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.preprocessor = Preprocessor(config_path)
        self.load_models()
        
    def load_models(self):
        logger.info("Loading models for inference...")
        path = self.config['paths']['artifacts']
        self.lstm_model = tf.keras.models.load_model(os.path.join(path, 'lstm_model.h5'))
        self.xgb_model = joblib.load(os.path.join(path, 'xgb_model.pkl'))
        self.preprocessor.load_artifacts()
        
        # Initialize SHAP explainer (using a small background sample if available, else TreeExplainer on model)
        # Note: TreeExplainer is fast for XGBoost
        self.explainer = shap.TreeExplainer(self.xgb_model)
        
    def predict(self, transaction_data: dict):
        """
        End-to-end prediction pipeline
        """
        # 1. Preprocess
        # Note: LSTM needs sequence. In this simulated real-time API, 
        # we lack the immediate state store to fetch the last 10 txns.
        # Strategy: We will mock the sequence by duplicating the current feature vector
        # or padding. A real production system uses a Feature Store (Redis/Feast).
        
        feature_vector = self.preprocessor.transform_single(transaction_data)
        
        # Prepare inputs
        xgb_input = feature_vector.reshape(1, -1)
        
        # Mock LSTM Sequence (1, 10, Features)
        lstm_input = np.tile(feature_vector, (1, self.config['data']['lookback'], 1))
        
        # 2. Inference
        lstm_score = float(self.lstm_model.predict(lstm_input, verbose=0)[0][0])
        xgb_score = float(self.xgb_model.predict_proba(xgb_input)[0][1])
        
        # 3. Hybrid Logic (AI + Domain Rules)
        final_score = 0.5 * lstm_score + 0.5 * xgb_score
        
        # --- DOMAIN RULE ENHANCEMENT ---
        # Real-world systems use "Veto Rules" alongside AI.
        # Rule: If DeviceID is strictly NOT in the user's history, boost risk.
        # (In this demo, we check if it matches the known 'safe' device)
        # 82:4e:8e:2a:9e:28 is the known safe device from our Mock App logic.
        
        # Note: In a production system, we would query the user's device history database.
        KNOWN_SAFE_DEVICE = "82:4e:8e:2a:9e:28"
        input_device = transaction_data.get("DeviceID", "")
        
        if input_device != KNOWN_SAFE_DEVICE:
            logger.warning(f"Domain Rule Triggered: Unknown Device {input_device}")
            # Boost the score significantly to reflect the high risk of account takeover
            final_score = max(final_score, 0.95)
            # Adjust factor explanation to show why
            sorted_factors["Unknown Device"] = 0.50 # High positive impact on risk
            
        # 4. Explainability
        shap_values = self.explainer.shap_values(xgb_input)
        # Get top contributing factors
        feature_names = self.preprocessor.feature_names
        factors = dict(zip(feature_names, shap_values[0].tolist()))
        
        # Sort factors by absolute impact
        sorted_factors = dict(sorted(factors.items(), key=lambda item: abs(item[1]), reverse=True)[:5])
        
        verdict = "ALLOW"
        if final_score > 0.8:
            verdict = "BLOCK"
        elif final_score > 0.5:
            verdict = "FLAG"
            
        return {
            "risk_score": final_score,
            "verdict": verdict,
            "lstm_score": lstm_score,
            "xgb_score": xgb_score,
            "factors": sorted_factors
        }
