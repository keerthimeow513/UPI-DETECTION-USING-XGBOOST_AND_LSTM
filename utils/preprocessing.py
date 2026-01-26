import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import joblib
import yaml
import os
from .logger import setup_logger

logger = setup_logger()

class Preprocessor:
    def __init__(self, config_path="07_configs/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        
    def feature_engineering(self, df):
        logger.info("Starting feature engineering...")
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Temporal Features
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
        df['DayOfMonth'] = df['Timestamp'].dt.day
        
        # Sorting
        df = df.sort_values(by=['SenderUPI', 'Timestamp'])
        
        # Lag Features
        df['TimeDiff'] = df.groupby('SenderUPI')['Timestamp'].diff().dt.total_seconds().fillna(0)
        df['AmountDiff'] = df.groupby('SenderUPI')['Amount'].diff().fillna(0)
        
        return df
        
    def fit_transform(self, df):
        logger.info("Fitting and transforming data...")
        df = self.feature_engineering(df)
        
        # Categorical
        for col in self.config['features']['categorical']:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.encoders[col] = le
            
        # Numerical
        num_cols = self.config['features']['numerical']
        scaler = MinMaxScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        self.scalers['scaler'] = scaler
        
        self.feature_names = num_cols + self.config['features']['categorical']
        
        # Save artifacts
        self.save_artifacts()
        return df
        
    def transform_single(self, data_dict):
        """Transform a single dictionary input for inference"""
        # Load artifacts if not in memory
        if not self.encoders:
            self.load_artifacts()
            
        # 1. Encode Categorical
        cat_features = []
        for col in self.config['features']['categorical']:
            val = str(data_dict.get(col, ''))
            try:
                # Handle unseen labels carefully
                encoded_val = self.encoders[col].transform([val])[0]
            except:
                encoded_val = 0 # Default for unknown
            cat_features.append(encoded_val)
            
        # 2. Scale Numerical
        # Note: In real-time, diff features (TimeDiff, AmountDiff) need history.
        # For this demo, we assume they are provided or default to 0.
        num_vals = [data_dict.get(col, 0) for col in self.config['features']['numerical']]
        num_scaled = self.scalers['scaler'].transform([num_vals])[0]
        
        return np.concatenate([num_scaled, cat_features])

    def create_sequences(self, df, lookback=None):
        if lookback is None:
            lookback = self.config['data']['lookback']
            
        logger.info(f"Creating sequences with lookback {lookback}...")
        
        X_lstm = []
        X_xgb = []
        y = []
        
        feature_cols = self.feature_names
        
        grouped = df.groupby('SenderUPI')
        
        for _, group in grouped:
            data = group[feature_cols].values
            target = group['IsFraud'].values
            
            if len(data) < lookback:
                continue
                
            for i in range(lookback, len(data)):
                X_lstm.append(data[i-lookback:i])
                X_xgb.append(data[i])
                y.append(target[i])
                
        return np.array(X_lstm), np.array(X_xgb), np.array(y)

    def save_artifacts(self):
        os.makedirs(self.config['paths']['artifacts'], exist_ok=True)
        joblib.dump(self.encoders, os.path.join(self.config['paths']['artifacts'], 'label_encoders.pkl'))
        joblib.dump(self.scalers['scaler'], os.path.join(self.config['paths']['artifacts'], 'scaler.pkl'))
        joblib.dump(self.feature_names, os.path.join(self.config['paths']['artifacts'], 'feature_names.pkl'))
        logger.info("Artifacts saved.")

    def load_artifacts(self):
        path = self.config['paths']['artifacts']
        self.encoders = joblib.load(os.path.join(path, 'label_encoders.pkl'))
        self.scalers['scaler'] = joblib.load(os.path.join(path, 'scaler.pkl'))
        self.feature_names = joblib.load(os.path.join(path, 'feature_names.pkl'))
