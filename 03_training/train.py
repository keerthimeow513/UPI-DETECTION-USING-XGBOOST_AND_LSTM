import os  # Import OS library for managing file paths and environment variables
# Disable GPU for training/inference stability on some envs to prevent CUDA errors
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import pandas as pd  # Import pandas for processing CSV datasets
import numpy as np   # Import numpy for numerical array handling
import tensorflow as tf  # Import TensorFlow for building and training deep learning models
from tensorflow.keras.models import Sequential  # Import Sequential for stacking neural network layers
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input  # Import specific neural layers for the sequence model
from tensorflow.keras.optimizers import Adam  # Import Adam optimizer for efficient gradient descent
import xgboost as xgb  # Import XGBoost for training gradient boosted decision trees
from sklearn.model_selection import train_test_split  # Import tool to split data into training/testing sets
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score  # Import evaluation metrics
import joblib  # Import joblib for saving non-Keras models like XGBoost
import yaml    # Import yaml for reading configuration files
import json    # Import json for saving performance metrics in a readable format
import sys     # Import sys for path manipulation

# Add project root to path so we can import 'utils'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocessing import Preprocessor  # Import our custom data preparation logic
from utils.logger import setup_logger         # Import our logging utility
from utils.security import generate_checksums_for_directory  # Import security utilities

logger = setup_logger()  # Initialize the logger for the training script


def load_config(path="07_configs/config.yaml"):
    """
    Helper function to load project settings from YAML config file.
    
    Args:
        path (str): Path to the YAML configuration file
        
    Returns:
        dict: Configuration parameters
        
    Raises:
        FileNotFoundError: If config file does not exist
        yaml.YAMLError: If config file is invalid
    """
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML configuration: {str(e)}")
        raise


def build_lstm(input_shape, config):
    """
    Function to define the architecture of the deep learning LSTM model.
    
    Creates a sequential neural network with LSTM layers for sequence modeling,
    dropout for regularization, and dense layers for output.
    
    Args:
        input_shape (tuple): Shape of input data (lookback_steps, n_features)
        config (dict): Model configuration parameters
        
    Returns:
        tf.keras.Model: Compiled LSTM model ready for training
    """
    model = Sequential([
        Input(shape=input_shape),
        LSTM(config['model']['lstm']['units_1'], return_sequences=True),
        Dropout(config['model']['lstm']['dropout']),
        LSTM(config['model']['lstm']['units_2']),
        Dropout(config['model']['lstm']['dropout']),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=config['model']['lstm']['learning_rate']),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model


def generate_model_checksums(artifacts_dir):
    """
    Generate SHA256 checksums for all saved model files.
    
    This function creates a checksums.json file that can be used
    to verify model integrity during inference.
    
    Args:
        artifacts_dir (str): Directory containing model files
        
    Returns:
        dict: Dictionary of filenames to checksums
    """
    checksums_file = os.path.join(artifacts_dir, 'checksums.json')
    
    try:
        checksums = generate_checksums_for_directory(
            directory=artifacts_dir,
            output_file=checksums_file,
            pattern='*'
        )
        logger.info(f"Generated checksums for {len(checksums)} files in {artifacts_dir}")
        return checksums
    except Exception as e:
        logger.error(f"Failed to generate checksums: {str(e)}")
        return {}


def train():
    """
    Main orchestration function for the model training pipeline.
    
    This function performs the complete training workflow:
    1. Loads and preprocesses data
    2. Creates sequences for LSTM
    3. Splits data into train/test sets
    4. Trains LSTM and XGBoost models
    5. Saves models and generates checksums for security
    6. Evaluates and saves metrics
    
    Raises:
        FileNotFoundError: If data file does not exist
        RuntimeError: If training fails
    """
    config = load_config()
    
    # 1. Load Data
    logger.info("Loading data...")
    try:
        df = pd.read_csv(config['paths']['raw_data'])
        logger.info(f"Loaded {len(df)} records from {config['paths']['raw_data']}")
    except FileNotFoundError:
        logger.error(f"Data file not found: {config['paths']['raw_data']}")
        raise
    
    # 2. Preprocess
    logger.info("Preprocessing data...")
    preprocessor = Preprocessor()
    df_processed = preprocessor.fit_transform(df)
    logger.info(f"Preprocessing complete. Shape: {df_processed.shape}")
    
    # 3. Create Sequences
    logger.info("Creating sequences for LSTM...")
    X_lstm, X_xgb, y = preprocessor.create_sequences(df_processed)
    logger.info(f"Sequence shapes - LSTM: {X_lstm.shape}, XGB: {X_xgb.shape}")
    
    # 4. Split Data
    logger.info("Splitting data into train/test sets...")
    X_lstm_train, X_lstm_test, X_xgb_train, X_xgb_test, y_train, y_test = train_test_split(
        X_lstm, X_xgb, y,
        test_size=config['data']['test_split'],
        random_state=42,
        stratify=y
    )
    logger.info(f"Train size: {len(y_train)}, Test size: {len(y_test)}")
    
    # Save training splits for debugging
    os.makedirs(config['paths']['processed_data'], exist_ok=True)
    np.save(os.path.join(config['paths']['processed_data'], 'X_xgb_train.npy'), X_xgb_train)
    
    # Ensure artifacts directory exists
    os.makedirs(config['paths']['artifacts'], exist_ok=True)
    
    # 5. Train LSTM
    logger.info("Training LSTM model...")
    neg = np.sum(y_train == 0)
    pos = np.sum(y_train == 1)
    total = neg + pos
    class_weight = {0: (1/neg)*(total/2.0), 1: (1/pos)*(total/2.0)}
    logger.info(f"Class distribution - Non-fraud: {neg}, Fraud: {pos}")
    
    lstm_model = build_lstm((X_lstm_train.shape[1], X_lstm_train.shape[2]), config)
    
    try:
        lstm_model.fit(
            X_lstm_train, y_train,
            epochs=config['model']['lstm']['epochs'],
            batch_size=config['model']['lstm']['batch_size'],
            validation_split=0.1,
            class_weight=class_weight,
            verbose=1
        )
        logger.info("LSTM training completed successfully")
    except Exception as e:
        logger.error(f"LSTM training failed: {str(e)}")
        raise RuntimeError(f"LSTM training failed: {str(e)}")
    
    # Save LSTM model
    lstm_path = os.path.join(config['paths']['artifacts'], 'lstm_model.h5')
    try:
        lstm_model.save(lstm_path)
        logger.info(f"LSTM model saved to {lstm_path}")
    except Exception as e:
        logger.error(f"Failed to save LSTM model: {str(e)}")
        raise
    
    # 6. Train XGBoost
    logger.info("Training XGBoost model...")
    scale_pos_weight = neg / pos if pos > 0 else 1.0
    
    xgb_model = xgb.XGBClassifier(
        n_estimators=config['model']['xgboost']['n_estimators'],
        max_depth=config['model']['xgboost']['max_depth'],
        learning_rate=config['model']['xgboost']['learning_rate'],
        scale_pos_weight=scale_pos_weight,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )
    
    try:
        xgb_model.fit(X_xgb_train, y_train)
        logger.info("XGBoost training completed successfully")
    except Exception as e:
        logger.error(f"XGBoost training failed: {str(e)}")
        raise RuntimeError(f"XGBoost training failed: {str(e)}")
    
    # Save XGBoost model using joblib (safer than pickle)
    xgb_path = os.path.join(config['paths']['artifacts'], 'xgb_model.pkl')
    try:
        joblib.dump(xgb_model, xgb_path)
        logger.info(f"XGBoost model saved to {xgb_path}")
    except Exception as e:
        logger.error(f"Failed to save XGBoost model: {str(e)}")
        raise
    
    # 7. Generate Checksums for Security
    logger.info("Generating checksums for model files...")
    try:
        checksums = generate_model_checksums(config['paths']['artifacts'])
        logger.info(f"Generated checksums for {len(checksums)} files")
        
        # Print checksums for verification
        print("\n" + "="*60)
        print("MODEL CHECKSUMS (SHA256)")
        print("="*60)
        for filename, checksum in sorted(checksums.items()):
            print(f"{filename:30} {checksum}")
        print("="*60 + "\n")
    except Exception as e:
        logger.warning(f"Failed to generate checksums: {str(e)}")
    
    # 8. Evaluate Hybrid Model
    logger.info("Evaluating hybrid model...")
    try:
        lstm_pred = lstm_model.predict(X_lstm_test).flatten()
        xgb_pred = xgb_model.predict_proba(X_xgb_test)[:, 1]
        hybrid_pred = 0.5 * lstm_pred + 0.5 * xgb_pred
        
        y_pred_class = (hybrid_pred > 0.5).astype(int)
        
        metrics = {
            "Accuracy": float(accuracy_score(y_test, y_pred_class)),
            "Precision": float(precision_score(y_test, y_pred_class)),
            "Recall": float(recall_score(y_test, y_pred_class)),
            "F1 Score": float(f1_score(y_test, y_pred_class)),
            "ROC AUC": float(roc_auc_score(y_test, hybrid_pred))
        }
        
        logger.info(f"Model Metrics: {metrics}")
        
        # Save metrics to JSON
        metrics_path = os.path.join(config['paths']['artifacts'], 'metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=4)
        logger.info(f"Metrics saved to {metrics_path}")
        
        # Print final summary
        print("\n" + "="*60)
        print("TRAINING COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Models saved to: {config['paths']['artifacts']}")
        print(f"\nFinal Metrics:")
        for metric, value in metrics.items():
            print(f"  {metric:12} {value:.4f}")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise RuntimeError(f"Model evaluation failed: {str(e)}")


if __name__ == "__main__":
    """Entry point for the training script."""
    try:
        train()
        logger.info("Training pipeline completed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Training pipeline failed: {str(e)}")
        print(f"\nERROR: Training failed - {str(e)}")
        sys.exit(1)
