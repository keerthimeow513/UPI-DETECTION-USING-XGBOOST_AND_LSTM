import sys  # Import system-specific parameters and functions
import os   # Import operating system interfaces for file path management

# Add project root to path so we can import from 'utils' even if we run this script from inside the '04_inference' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable GPU completely for TensorFlow to ensure stability and avoid library conflicts in production/CPU environments
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf  # Import TensorFlow for running the deep learning LSTM model
import joblib            # Import joblib for loading serialized model files (.pkl)
import numpy as np       # Import numpy for matrix and array operations
import yaml              # Import yaml for reading the configuration file
import shap              # Import SHAP (SHapley Additive Explanations) for model transparency/explainability
from utils.preprocessing import Preprocessor  # Import our custom data transformation class
from utils.logger import setup_logger         # Import our custom logging utility
from utils.security import (
    SecureModelLoader,
    calculate_checksum,
    validate_model_integrity,
    secure_load_pickle,
    ModelSecurityError
)
from utils.feature_store import UserFeatureStore, get_feature_store  # Import feature store for real user history

logger = setup_logger()  # Initialize the logger for this service


class ModelLoadingError(Exception):
    """Custom exception for model loading failures."""
    pass


class FraudDetectionService:
    """
    Main service class that orchestrates fraud prediction with secure model loading.
    
    This service loads trained ML models and performs end-to-end fraud detection
    including preprocessing, inference, and explainability. It implements security
    features like checksum validation and restricted unpickling.
    
    Attributes:
        config (dict): Configuration parameters loaded from YAML
        preprocessor (Preprocessor): Data preprocessing instance
        lstm_model: Loaded LSTM TensorFlow model
        xgb_model: Loaded XGBoost model
        explainer: SHAP explainer for model interpretability
        secure_loader (SecureModelLoader): Secure model loader with integrity checks
    """
    
    def __init__(self, config_path="07_configs/config.yaml"):
        """
        Initialize the Fraud Detection Service.
        
        Args:
            config_path (str): Path to the configuration YAML file
            
        Raises:
            ModelLoadingError: If models cannot be loaded
        """
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise ModelLoadingError(
                f"Configuration file not found: {config_path}\n"
                f"Please ensure the config file exists at the specified path."
            )
        except yaml.YAMLError as e:
            raise ModelLoadingError(f"Invalid YAML in config file: {str(e)}")
        
        self.preprocessor = Preprocessor(config_path)
        self.lstm_model = None
        self.xgb_model = None
        self.explainer = None
        self.secure_loader = None
        self.feature_store = None
        
        # Load models with security checks
        self.load_models()
        
        # Initialize feature store for real user transaction history
        try:
            self.feature_store = get_feature_store()
            if self.feature_store.enabled:
                logger.info("Feature store initialized for real user history")
            else:
                logger.warning("Feature store disabled - using mocked history")
        except Exception as e:
            logger.warning(f"Failed to initialize feature store: {str(e)}")
            self.feature_store = None
    
    def load_models(self):
        """
        Load all trained AI models and supporting artifacts with security validation.
        
        This method performs secure model loading including:
        - File existence checks
        - SHA256 checksum validation
        - Restricted unpickling for pickle files
        - Clear error messages for troubleshooting
        
        Raises:
            ModelLoadingError: If any model fails to load or validation fails
        """
        logger.info("Loading models for inference with security validation...")
        
        path = self.config['paths']['artifacts']
        
        # Check if artifacts directory exists
        if not os.path.exists(path):
            raise ModelLoadingError(
                f"Artifacts directory not found: {path}\n"
                f"Please ensure models have been trained. Run: python 03_training/train.py"
            )
        
        # Initialize secure model loader
        checksums_file = os.path.join(path, 'checksums.json')
        try:
            self.secure_loader = SecureModelLoader(
                models_dir=path,
                checksums_file=checksums_file if os.path.exists(checksums_file) else None,
                verify_checksums=os.path.exists(checksums_file)
            )
        except Exception as e:
            logger.warning(f"Failed to initialize secure loader: {str(e)}")
            self.secure_loader = None
        
        # Define expected model files
        lstm_path = os.path.join(path, 'lstm_model.h5')
        xgb_path = os.path.join(path, 'xgb_model.pkl')
        
        # Check file existence before loading
        missing_files = []
        if not os.path.exists(lstm_path):
            missing_files.append('lstm_model.h5')
        if not os.path.exists(xgb_path):
            missing_files.append('xgb_model.pkl')
        
        if missing_files:
            raise ModelLoadingError(
                f"Required model files not found: {', '.join(missing_files)}\n"
                f"Location: {path}\n"
                f"\nPlease ensure models have been trained and saved correctly.\n"
                f"Run the training script: python 03_training/train.py\n"
                f"\nTo verify model files exist, check:\n"
                f"  ls -la {path}"
            )
        
        # Load LSTM model (TensorFlow/Keras - no pickle vulnerability)
        try:
            logger.info(f"Loading LSTM model from {lstm_path}...")
            self.lstm_model = tf.keras.models.load_model(lstm_path)
            logger.info("LSTM model loaded successfully")
        except Exception as e:
            raise ModelLoadingError(
                f"Failed to load LSTM model: {str(e)}\n"
                f"The model file may be corrupted. Try retraining: python 03_training/train.py"
            )
        
        # Load XGBoost model with secure unpickler
        try:
            logger.info(f"Loading XGBoost model from {xgb_path}...")
            
            # Try using secure loader first
            if self.secure_loader:
                self.xgb_model = self.secure_loader.load_model('xgb_model.pkl')
            else:
                # Fallback to secure_load_pickle
                self.xgb_model = secure_load_pickle(xgb_path)
            
            logger.info("XGBoost model loaded successfully")
        except ModelSecurityError as e:
            raise ModelLoadingError(
                f"Security violation while loading XGBoost model: {str(e)}\n"
                f"The model file may have been tampered with.\n"
                f"Please regenerate the model by running: python 03_training/train.py"
            )
        except Exception as e:
            # Fallback to joblib with warning
            logger.warning(f"Secure loading failed, using joblib fallback: {str(e)}")
            try:
                self.xgb_model = joblib.load(xgb_path)
                logger.info("XGBoost model loaded via joblib (without integrity verification)")
            except Exception as e2:
                raise ModelLoadingError(
                    f"Failed to load XGBoost model: {str(e2)}\n"
                    f"The model file may be corrupted. Try retraining: python 03_training/train.py"
                )
        
        # Load preprocessor artifacts
        try:
            logger.info("Loading preprocessor artifacts...")
            self.preprocessor.load_artifacts()
            logger.info("Preprocessor artifacts loaded successfully")
        except FileNotFoundError as e:
            raise ModelLoadingError(
                f"Preprocessor artifacts not found: {str(e)}\n"
                f"Please ensure training has been completed to generate artifacts."
            )
        except Exception as e:
            raise ModelLoadingError(
                f"Failed to load preprocessor artifacts: {str(e)}\n"
                f"The artifacts may be corrupted. Try retraining: python 03_training/train.py"
            )
        
        # Initialize SHAP explainer
        try:
            logger.info("Initializing SHAP explainer...")
            self.explainer = shap.TreeExplainer(self.xgb_model)
            logger.info("SHAP explainer initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize SHAP explainer: {str(e)}")
            self.explainer = None
        
        logger.info("All models loaded successfully with security validation")
    
    def validate_model_integrity(self, file_path: str, expected_checksum: str = None) -> bool:
        """
        Validate the integrity of a model file.
        
        Args:
            file_path (str): Path to the model file
            expected_checksum (str): Expected SHA256 checksum
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        if not expected_checksum:
            logger.warning(f"No checksum provided for {file_path}, skipping integrity check")
            return True
        
        try:
            return validate_model_integrity(file_path, expected_checksum)
        except Exception as e:
            logger.error(f"Integrity validation failed: {str(e)}")
            return False
    
    def predict(self, transaction_data: dict):
        """
        End-to-end prediction pipeline with fraud risk assessment.
        
        Args:
            transaction_data (dict): Raw transaction data containing features
                like Amount, DeviceID, SenderUPI, etc.
        
        Returns:
            dict: Prediction results including:
                - risk_score: Combined fraud probability (0-1)
                - verdict: Final decision (ALLOW/FLAG/BLOCK)
                - lstm_score: LSTM model probability
                - xgb_score: XGBoost model probability
                - factors: Top 5 contributing factors
        
        Raises:
            ValueError: If required features are missing
            RuntimeError: If prediction fails
        """
        # Validate models are loaded
        if self.lstm_model is None or self.xgb_model is None:
            raise RuntimeError("Models not loaded. Please check initialization.")
        
        try:
            # 1. Preprocess the incoming raw dictionary into a numerical vector
            feature_vector = self.preprocessor.transform_single(transaction_data)
            
            # Prepare inputs for the XGBoost model (Needs 2D: [1, n_features])
            xgb_input = feature_vector.reshape(1, -1)
            
            # 2. Get user ID and retrieve real transaction history from feature store
            user_id = transaction_data.get('SenderUPI', 'unknown')
            lstm_history = None
            velocity_features = {}
            
            if self.feature_store and self.feature_store.enabled:
                # Get real user history for LSTM
                lstm_history = self.feature_store.get_history(user_id)
                
                # Compute velocity features for enhanced fraud detection
                txns_last_hour = self.feature_store.get_transaction_count(user_id, hours=1)
                txns_last_24h = self.feature_store.get_transaction_count(user_id, hours=24)
                amount_last_hour = self.feature_store.get_amount_in_window(user_id, hours=1)
                
                velocity_features = {
                    'transactions_last_hour': txns_last_hour,
                    'transactions_last_24h': txns_last_24h,
                    'amount_last_hour': amount_last_hour
                }
                
                logger.debug(f"User {user_id} velocity features: {velocity_features}")
            
            # 3. Prepare LSTM input (Needs 3D: [1, sequence_length, n_features])
            if lstm_history is not None:
                # Use real user history
                lstm_input = lstm_history.reshape(1, self.config['data']['lookback'], -1)
                logger.debug(f"Using real history for user {user_id}")
            else:
                # Not enough history - use current features padded (fallback)
                lstm_input = np.tile(feature_vector, (1, self.config['data']['lookback'], 1))
                logger.debug(f"Using padded history for user {user_id}")
            
            # 4. Run Inference through both models
            lstm_score = float(self.lstm_model.predict(lstm_input, verbose=0)[0][0])
            xgb_score = float(self.xgb_model.predict_proba(xgb_input)[0][1])
            
            # 3. Hybrid Logic (Average the AI scores)
            final_score = 0.5 * lstm_score + 0.5 * xgb_score
            
            # 4. Explainability (Calculate SHAP values for the current transaction)
            factors = {}
            if self.explainer:
                try:
                    shap_values = self.explainer.shap_values(xgb_input)
                    feature_names = self.preprocessor.feature_names
                    factors = dict(zip(feature_names, shap_values[0].tolist()))
                    
                    # Sort factors by their absolute impact to find the top 5 most important reasons
                    factors = dict(sorted(factors.items(), key=lambda item: abs(item[1]), reverse=True)[:5])
                except Exception as e:
                    logger.warning(f"SHAP explanation failed: {str(e)}")
            
            # --- DOMAIN RULE ENHANCEMENT (Hybrid Safety Layer) ---
            # Load security settings from config
            security_config = self.config.get('security', {})
            known_safe_devices = security_config.get('known_safe_devices', [])
            risk_thresholds = security_config.get('risk_thresholds', {'block': 0.8, 'flag': 0.5})
            amount_thresholds = security_config.get('amount_thresholds', {'high': 10000, 'critical': 50000})
            unusual_hours = security_config.get('unusual_hours', {'start': 0, 'end': 5})
            velocity_thresholds = security_config.get('velocity_thresholds', {
                'transactions_per_hour': 5,
                'amount_per_hour': 50000
            })
            
            input_device = transaction_data.get("DeviceID", "")
            amount = transaction_data.get("Amount", 0)
            hour = transaction_data.get("Hour", 12)
            
            # Rule 1: Velocity-Based Checks (using real history from feature store)
            txns_last_hour = velocity_features.get('transactions_last_hour', 0)
            amount_last_hour = velocity_features.get('amount_last_hour', 0)
            
            if txns_last_hour > velocity_thresholds.get('transactions_per_hour', 5):
                logger.warning(f"Domain Rule Triggered: High Velocity ({txns_last_hour} txns/hour)")
                final_score = max(final_score, 0.85)
                factors[f"High Transaction Velocity ({txns_last_hour}/hour)"] = 0.45
            
            if amount_last_hour > velocity_thresholds.get('amount_per_hour', 50000):
                logger.warning(f"Domain Rule Triggered: High Amount Velocity (₹{amount_last_hour}/hour)")
                final_score = max(final_score, 0.75)
                factors[f"High Amount Velocity (₹{amount_last_hour:.0f}/hour)"] = 0.35
            
            # Rule 2: Unknown Device Check
            is_known_device = input_device in known_safe_devices
            if not is_known_device:
                logger.warning(f"Domain Rule Triggered: Unknown Device {input_device}")
                
                # Context-Aware Decision for Unknown Device:
                if final_score > 0.4 or amount > amount_thresholds.get('high', 10000):
                    final_score = max(final_score, 0.95)
                    factors["Unknown Device + High Risk"] = 0.50
                else:
                    final_score = max(final_score, 0.6)
                    factors["New Device (OTP Required)"] = 0.30
            
            # Rule 3: Unusual Hour + High Amount Check
            elif amount > amount_thresholds.get('high', 10000) and \
                 (hour < unusual_hours.get('end', 5) or hour > 23):
                logger.warning(f"Domain Rule Triggered: High Amount at Unusual Hour")
                final_score = max(final_score, 0.6)
                factors["Unusual Hour + High Amount"] = 0.40
            
            # 5. Determine the Verdict based on the final risk score
            verdict = "ALLOW"
            if final_score > risk_thresholds.get('block', 0.8):
                verdict = "BLOCK"
            elif final_score > risk_thresholds.get('flag', 0.5):
                verdict = "FLAG"
            
            # 6. Store transaction in feature store for future history
            if self.feature_store and self.feature_store.enabled:
                try:
                    self.feature_store.add_transaction(user_id, feature_vector)
                    logger.debug(f"Stored transaction for user {user_id}")
                except Exception as e:
                    logger.warning(f"Failed to store transaction for user {user_id}: {str(e)}")
            
            return {
                "risk_score": final_score,
                "verdict": verdict,
                "lstm_score": lstm_score,
                "xgb_score": xgb_score,
                "factors": factors,
                "velocity_features": velocity_features if velocity_features else None
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise RuntimeError(f"Failed to process transaction: {str(e)}")
