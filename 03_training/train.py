import os # Import OS library for managing file paths and environment variables
# Disable GPU for training/inference stability on some envs to prevent CUDA errors
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import pandas as pd # Import pandas for processing CSV datasets
import numpy as np # Import numpy for numerical array handling
import tensorflow as tf # Import TensorFlow for building and training deep learning models
from tensorflow.keras.models import Sequential # Import Sequential for stacking neural network layers
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input # Import specific neural layers for the sequence model
from tensorflow.keras.optimizers import Adam # Import Adam optimizer for efficient gradient descent
import xgboost as xgb # Import XGBoost for training gradient boosted decision trees
from sklearn.model_selection import train_test_split # Import tool to split data into training and testing sets
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score # Import evaluation metrics
import joblib # Import joblib for saving non-Keras models like XGBoost
import yaml # Import yaml for reading configuration files
import json # Import json for saving performance metrics in a readable format
import sys # Import sys for path manipulation

# Add project root to path so we can import 'utils'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocessing import Preprocessor # Import our custom data preparation logic
from utils.logger import setup_logger # Import our logging utility

logger = setup_logger() # Initialize the logger for the training script

def load_config(path="07_configs/config.yaml"): # Helper function to load project settings
    with open(path, 'r') as f: # Open the YAML file
        return yaml.safe_load(f) # Convert YAML to a Python dictionary

def build_lstm(input_shape, config): # Function to define the architecture of the deep learning model
    model = Sequential([ # Create a sequential model container
        Input(shape=input_shape), # Define the input shape (lookback_steps, number_of_features)
        LSTM(config['model']['lstm']['units_1'], return_sequences=True), # First LSTM layer; returns sequences for the next layer
        Dropout(config['model']['lstm']['dropout']), # Dropout layer to prevent overfitting by randomly disabling neurons
        LSTM(config['model']['lstm']['units_2']), # Second LSTM layer; returns a single flat vector
        Dropout(config['model']['lstm']['dropout']), # Another dropout layer for regularization
        Dense(16, activation='relu'), # Intermediate dense layer for feature extraction
        Dense(1, activation='sigmoid') # Final output layer with sigmoid to produce a probability (0-1)
    ])
    # Compile the model with binary cross-entropy loss suitable for fraud detection (binary classification)
    model.compile(optimizer=Adam(learning_rate=config['model']['lstm']['learning_rate']),
                  loss='binary_crossentropy', metrics=['accuracy'])
    return model # Return the ready-to-train model

def train(): # The main orchestration function for the training pipeline
    config = load_config() # Load hyperparameters and file paths from config
    
    # 1. Load Data
    logger.info("Loading data...") # Log status
    df = pd.read_csv(config['paths']['raw_data']) # Read the raw transaction CSV into a DataFrame
    
    # 2. Preprocess
    preprocessor = Preprocessor() # Initialize the preprocessing engine
    df_processed = preprocessor.fit_transform(df) # Engineering features, scale data, and save encoders
    
    # 3. Create Sequences
    # Restructure data into 3D (for LSTM) and 2D (for XGBoost) formats
    X_lstm, X_xgb, y = preprocessor.create_sequences(df_processed)
    
    # 4. Split Data
    # Split into 80% training and 20% testing. 'stratify=y' ensures equal fraud ratio in both sets.
    X_lstm_train, X_lstm_test, X_xgb_train, X_xgb_test, y_train, y_test = train_test_split(
        X_lstm, X_xgb, y, test_size=config['data']['test_split'], random_state=42, stratify=y
    )
    
    # Save training splits as numpy files for debugging or reproducibility
    os.makedirs(config['paths']['processed_data'], exist_ok=True)
    np.save(os.path.join(config['paths']['processed_data'], 'X_xgb_train.npy'), X_xgb_train)
    
    # 5. Train LSTM
    logger.info("Training LSTM...") # Log status
    neg = np.sum(y_train == 0) # Count non-fraudulent cases
    pos = np.sum(y_train == 1) # Count fraudulent cases
    total = neg + pos # Total number of training samples
    # Calculate weights to tell the model to pay more attention to the rare fraud cases
    class_weight = {0: (1/neg)*(total/2.0), 1: (1/pos)*(total/2.0)}
    
    # Build the LSTM model based on training data shape
    lstm_model = build_lstm((X_lstm_train.shape[1], X_lstm_train.shape[2]), config)
    # Start the training process
    lstm_model.fit(
        X_lstm_train, y_train,
        epochs=config['model']['lstm']['epochs'], # Number of passes through the full dataset
        batch_size=config['model']['lstm']['batch_size'], # Samples processed before updating weights
        validation_split=0.1, # Use 10% of training data for real-time validation
        class_weight=class_weight, # Apply the fraud-priority weights
        verbose=1 # Show progress bar
    )
    # Save the trained deep learning model to a file
    lstm_model.save(os.path.join(config['paths']['artifacts'], 'lstm_model.h5'))
    
    # 6. Train XGBoost
    logger.info("Training XGBoost...") # Log status
    scale_pos_weight = neg / pos # Calculate the ratio of normal to fraud to balance the tree learning
    xgb_model = xgb.XGBClassifier( # Initialize the tree classifier with config parameters
        n_estimators=config['model']['xgboost']['n_estimators'], # Number of trees to build
        max_depth=config['model']['xgboost']['max_depth'], # Maximum depth of each tree
        learning_rate=config['model']['xgboost']['learning_rate'], # Step size shrinkage
        scale_pos_weight=scale_pos_weight, # Balancing weight for imbalanced data
        use_label_encoder=False, # Disable legacy features
        eval_metric='logloss' # Evaluation metric used during training
    )
    xgb_model.fit(X_xgb_train, y_train) # Fit the XGBoost model on the flat feature set
    # Save the trained XGBoost model to a pickle file
    joblib.dump(xgb_model, os.path.join(config['paths']['artifacts'], 'xgb_model.pkl'))
    
    # 7. Evaluate Hybrid
    logger.info("Evaluating Hybrid Model...") # Log status
    lstm_pred = lstm_model.predict(X_lstm_test).flatten() # Generate probabilities from LSTM
    xgb_pred = xgb_model.predict_proba(X_xgb_test)[:, 1] # Generate probabilities from XGBoost
    # Average the two models (Ensemble) for a more robust final prediction
    hybrid_pred = 0.5 * lstm_pred + 0.5 * xgb_pred
    
    # Convert probabilities to 0 or 1 based on a 0.5 threshold
    y_pred_class = (hybrid_pred > 0.5).astype(int)
    # Calculate a variety of performance metrics
    metrics = {
        "Accuracy": float(accuracy_score(y_test, y_pred_class)), # Overall correctness
        "Precision": float(precision_score(y_test, y_pred_class)), # How many predicted frauds were actually fraud
        "Recall": float(recall_score(y_test, y_pred_class)), # How many actual frauds were caught
        "F1 Score": float(f1_score(y_test, y_pred_class)), # Balance between precision and recall
        "ROC AUC": float(roc_auc_score(y_test, hybrid_pred)) # Quality of the model across all thresholds
    }
    
    logger.info(f"Metrics: {metrics}") # Print metrics to the log
    # Save the metrics to a JSON file for later analysis/dashboarding
    with open(os.path.join(config['paths']['artifacts'], 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__": # Entry point
    train() # Run the training script
