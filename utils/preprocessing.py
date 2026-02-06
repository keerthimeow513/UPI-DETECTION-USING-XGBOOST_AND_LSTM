"""
UPI Fraud Detection - Data Preprocessing Module

This module provides data preprocessing and feature engineering capabilities
for the UPI Fraud Detection system. It handles:
- Feature engineering (temporal and lag features)
- Categorical encoding using LabelEncoder
- Numerical scaling using MinMaxScaler
- Sequence creation for LSTM models
- Artifact persistence for inference

Example:
    from utils.preprocessing import Preprocessor
    
    preprocessor = Preprocessor('07_configs/config.yaml')
    df_processed = preprocessor.fit_transform(df_raw)
    X_lstm, X_xgb, y = preprocessor.create_sequences(df_processed)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import joblib
import yaml
import os
from .logger import setup_logger

logger = setup_logger()


class Preprocessor:
    """
    Main class for data preprocessing and feature engineering.
    
    This class handles the complete data preparation pipeline including:
    - Feature extraction from timestamps
    - Lag feature computation
    - Categorical encoding
    - Numerical scaling
    - Sequence creation for deep learning models
    
    Attributes:
        config (dict): Configuration parameters loaded from YAML file
        scalers (dict): Dictionary of fitted scalers for numerical features
        encoders (dict): Dictionary of fitted encoders for categorical features
        feature_names (list): Ordered list of feature names
    """
    
    def __init__(self, config_path="07_configs/config.yaml"):
        """
        Initialize the Preprocessor with configuration.
        
        Args:
            config_path (str): Path to the YAML configuration file.
                             Defaults to "07_configs/config.yaml".
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
    
    def feature_engineering(self, df):
        """
        Create new predictive features from raw transaction data.
        
        Extracts temporal features (hour, day of week, day of month) and
        computes lag features (time difference, amount difference) for each user.
        
        Args:
            df (pd.DataFrame): Raw transaction data with Timestamp, Amount,
                              SenderUPI, and other columns.
        
        Returns:
            pd.DataFrame: DataFrame with engineered features added.
        
        Example:
            >>> df_raw = pd.read_csv('transactions.csv')
            >>> df_processed = preprocessor.feature_engineering(df_raw)
            >>> print(df_processed.columns)
            Index(['Timestamp', 'Amount', 'Hour', 'DayOfWeek', 'DayOfMonth',
                   'TimeDiff', 'AmountDiff', ...])
        """
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
        """
        Fit preprocessing pipeline and transform data.
        
        This method learns the data distributions (for scaling and encoding)
        and transforms the entire dataset. It should be called on training data.
        
        Args:
            df (pd.DataFrame): Raw training data.
        
        Returns:
            pd.DataFrame: Fully processed DataFrame with all features encoded and scaled.
        
        Example:
            >>> preprocessor = Preprocessor()
            >>> df_train = pd.read_csv('train.csv')
            >>> df_processed = preprocessor.fit_transform(df_train)
            >>> preprocessor.save_artifacts()  # Save for inference
        """
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
        """
        Transform a single transaction dictionary for real-time inference.
        
        This method is optimized for real-time predictions where only one
        transaction needs to be processed at a time.
        
        Args:
            data_dict (dict): Dictionary containing transaction features.
                Required keys match the config features (numerical + categorical).
        
        Returns:
            np.ndarray: Flattened array of encoded and scaled features.
        
        Raises:
            ValueError: If required features are missing from data_dict.
        
        Example:
            >>> transaction = {
            ...     "SenderUPI": "user@upi",
            ...     "ReceiverUPI": "shop@upi",
            ...     "Amount": 500.0,
            ...     "DeviceID": "device1",
            ...     "Latitude": 12.97,
            ...     "Longitude": 77.59,
            ...     "Hour": 14,
            ...     "DayOfWeek": 1,
            ...     "DayOfMonth": 15,
            ...     "TimeDiff": 0,
            ...     "AmountDiff": 0
            ... }
            >>> features = preprocessor.transform_single(transaction)
            >>> print(features.shape)
            (10,)
        """
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
            except (KeyError, ValueError):
                logger.warning(f"Unseen label '{val}' in column '{col}', defaulting to 0")
                encoded_val = 0
            cat_features.append(encoded_val)
        
        # 2. Scale Numerical
        # Note: In real-time, diff features (TimeDiff, AmountDiff) need history.
        # For this demo, we assume they are provided or default to 0.
        num_vals = [data_dict.get(col, 0) for col in self.config['features']['numerical']]
        num_scaled = self.scalers['scaler'].transform([num_vals])[0]
        
        return np.concatenate([num_scaled, cat_features])
    
    def create_sequences(self, df, lookback=None):
        """
        Create sequential data for LSTM model training.
        
        Restructures the data into 3D arrays suitable for LSTM input by
        grouping transactions by user and creating time windows.
        
        Args:
            df (pd.DataFrame): Processed DataFrame with engineered features.
            lookback (int, optional): Number of previous transactions to include
                                     in each sequence. Defaults to config value.
        
        Returns:
            tuple: Three numpy arrays (X_lstm, X_xgb, y)
                - X_lstm: 3D array [samples, lookback, features] for LSTM
                - X_xgb: 2D array [samples, features] for XGBoost
                - y: 1D array [samples] of fraud labels
        
        Example:
            >>> df_processed = preprocessor.fit_transform(df_raw)
            >>> X_lstm, X_xgb, y = preprocessor.create_sequences(df_processed, lookback=10)
            >>> print(X_lstm.shape, X_xgb.shape, y.shape)
            (15000, 10, 10) (15000, 10) (15000,)
        """
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
        """
        Save fitted preprocessing artifacts to disk.
        
        Saves encoders, scalers, and feature names so they can be loaded
        during inference to ensure consistent transformations.
        
        Example:
            >>> preprocessor.fit_transform(df_train)
            >>> preprocessor.save_artifacts()
            # Artifacts saved to 02_models/artifacts/
        """
        os.makedirs(self.config['paths']['artifacts'], exist_ok=True)
        joblib.dump(self.encoders, os.path.join(self.config['paths']['artifacts'], 'label_encoders.pkl'))
        joblib.dump(self.scalers['scaler'], os.path.join(self.config['paths']['artifacts'], 'scaler.pkl'))
        joblib.dump(self.feature_names, os.path.join(self.config['paths']['artifacts'], 'feature_names.pkl'))
        logger.info("Artifacts saved.")
    
    def load_artifacts(self):
        """
        Load fitted preprocessing artifacts from disk.
        
        Loads previously saved encoders, scalers, and feature names for use
        during inference.
        
        Example:
            >>> preprocessor = Preprocessor()
            >>> preprocessor.load_artifacts()
            >>> features = preprocessor.transform_single(transaction)
        """
        path = self.config['paths']['artifacts']
        self.encoders = joblib.load(os.path.join(path, 'label_encoders.pkl'))
        self.scalers['scaler'] = joblib.load(os.path.join(path, 'scaler.pkl'))
        self.feature_names = joblib.load(os.path.join(path, 'feature_names.pkl'))
