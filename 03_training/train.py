import os
# Disable GPU for training/inference stability on some envs
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
import joblib
import yaml
import json
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocessing import Preprocessor
from utils.logger import setup_logger

logger = setup_logger()

def load_config(path="07_configs/config.yaml"):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def build_lstm(input_shape, config):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(config['model']['lstm']['units_1'], return_sequences=True),
        Dropout(config['model']['lstm']['dropout']),
        LSTM(config['model']['lstm']['units_2']),
        Dropout(config['model']['lstm']['dropout']),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(learning_rate=config['model']['lstm']['learning_rate']),
                  loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train():
    config = load_config()
    
    # 1. Load Data
    logger.info("Loading data...")
    df = pd.read_csv(config['paths']['raw_data'])
    
    # 2. Preprocess
    preprocessor = Preprocessor()
    df_processed = preprocessor.fit_transform(df)
    
    # 3. Create Sequences
    X_lstm, X_xgb, y = preprocessor.create_sequences(df_processed)
    
    # 4. Split
    # Using stratify to maintain class balance
    X_lstm_train, X_lstm_test, X_xgb_train, X_xgb_test, y_train, y_test = train_test_split(
        X_lstm, X_xgb, y, test_size=config['data']['test_split'], random_state=42, stratify=y
    )
    
    # Save splits for reproducibility/testing
    os.makedirs(config['paths']['processed_data'], exist_ok=True)
    np.save(os.path.join(config['paths']['processed_data'], 'X_xgb_train.npy'), X_xgb_train)
    # ... (save others if needed)
    
    # 5. Train LSTM
    logger.info("Training LSTM...")
    neg = np.sum(y_train == 0)
    pos = np.sum(y_train == 1)
    total = neg + pos
    class_weight = {0: (1/neg)*(total/2.0), 1: (1/pos)*(total/2.0)}
    
    lstm_model = build_lstm((X_lstm_train.shape[1], X_lstm_train.shape[2]), config)
    lstm_model.fit(
        X_lstm_train, y_train,
        epochs=config['model']['lstm']['epochs'],
        batch_size=config['model']['lstm']['batch_size'],
        validation_split=0.1,
        class_weight=class_weight,
        verbose=1
    )
    lstm_model.save(os.path.join(config['paths']['artifacts'], 'lstm_model.h5'))
    
    # 6. Train XGBoost
    logger.info("Training XGBoost...")
    scale_pos_weight = neg / pos
    xgb_model = xgb.XGBClassifier(
        n_estimators=config['model']['xgboost']['n_estimators'],
        max_depth=config['model']['xgboost']['max_depth'],
        learning_rate=config['model']['xgboost']['learning_rate'],
        scale_pos_weight=scale_pos_weight,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    xgb_model.fit(X_xgb_train, y_train)
    joblib.dump(xgb_model, os.path.join(config['paths']['artifacts'], 'xgb_model.pkl'))
    
    # 7. Evaluate Hybrid
    logger.info("Evaluating Hybrid Model...")
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
    
    logger.info(f"Metrics: {metrics}")
    with open(os.path.join(config['paths']['artifacts'], 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    train()
