"""Unit tests for preprocessing module."""

import unittest
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.preprocessing import Preprocessor


class TestPreprocessor(unittest.TestCase):
    """Test cases for the Preprocessor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.config_path = os.path.join(os.path.dirname(__file__), '../../07_configs/config.yaml')
        cls.sample_data = pd.DataFrame({
            'TransactionID': ['tx1', 'tx2', 'tx3'],
            'Timestamp': [datetime.now(), datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=2)],
            'SenderName': ['User A', 'User B', 'User C'],
            'SenderUPI': ['usera@upi', 'userb@upi', 'userc@upi'],
            'ReceiverName': ['Shop X', 'Shop Y', 'Shop Z'],
            'ReceiverUPI': ['shopx@upi', 'shopy@upi', 'shopz@upi'],
            'Amount': [100.0, 500.0, 1000.0],
            'DeviceID': ['device1', 'device2', 'device3'],
            'Latitude': [12.97, 13.08, 12.92],
            'Longitude': [77.59, 80.27, 77.62],
            'IsFraud': [0, 0, 1]
        })
    
    def test_preprocessor_initialization(self):
        """Test that Preprocessor initializes correctly."""
        preprocessor = Preprocessor(self.config_path)
        self.assertIsNotNone(preprocessor.config)
        self.assertIsInstance(preprocessor.scalers, dict)
        self.assertIsInstance(preprocessor.encoders, dict)
        self.assertIsInstance(preprocessor.feature_names, list)
    
    def test_feature_engineering(self):
        """Test feature engineering creates expected features."""
        preprocessor = Preprocessor(self.config_path)
        df_processed = preprocessor.feature_engineering(self.sample_data.copy())
        
        # Check that temporal features are created
        self.assertIn('Hour', df_processed.columns)
        self.assertIn('DayOfWeek', df_processed.columns)
        self.assertIn('DayOfMonth', df_processed.columns)
        
        # Check that lag features are created
        self.assertIn('TimeDiff', df_processed.columns)
        self.assertIn('AmountDiff', df_processed.columns)
        
        # Check data types
        self.assertTrue(pd.api.types.is_numeric_dtype(df_processed['Hour']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df_processed['DayOfWeek']))
    
    def test_fit_transform(self):
        """Test fit_transform method."""
        preprocessor = Preprocessor(self.config_path)
        df_processed = preprocessor.fit_transform(self.sample_data.copy())
        
        # Check that data is returned
        self.assertIsInstance(df_processed, pd.DataFrame)
        self.assertGreater(len(df_processed), 0)
        
        # Check that encoders and scalers are populated
        self.assertGreater(len(preprocessor.encoders), 0)
        self.assertGreater(len(preprocessor.scalers), 0)
        self.assertGreater(len(preprocessor.feature_names), 0)
    
    def test_transform_single(self):
        """Test transform_single method."""
        preprocessor = Preprocessor(self.config_path)
        
        # First fit on sample data to create encoders
        preprocessor.fit_transform(self.sample_data.copy())
        
        # Then transform a single transaction
        transaction = {
            'SenderUPI': 'usera@upi',
            'ReceiverUPI': 'shopx@upi',
            'Amount': 500.0,
            'DeviceID': 'device1',
            'Latitude': 12.97,
            'Longitude': 77.59,
            'Hour': 14,
            'DayOfWeek': 1,
            'DayOfMonth': 15,
            'TimeDiff': 0,
            'AmountDiff': 0
        }
        
        result = preprocessor.transform_single(transaction)
        
        # Check that result is a numpy array
        self.assertIsInstance(result, np.ndarray)
        # Check that result has expected number of features
        self.assertEqual(len(result), len(preprocessor.feature_names))
    
    def test_transform_single_unseen_label(self):
        """Test transform_single handles unseen labels gracefully."""
        preprocessor = Preprocessor(self.config_path)
        
        # First fit on sample data
        preprocessor.fit_transform(self.sample_data.copy())
        
        # Transform with unseen label
        transaction = {
            'SenderUPI': 'newuser@upi',  # Unseen label
            'ReceiverUPI': 'newshop@upi',  # Unseen label
            'Amount': 500.0,
            'DeviceID': 'newdevice',
            'Latitude': 12.97,
            'Longitude': 77.59,
            'Hour': 14,
            'DayOfWeek': 1,
            'DayOfMonth': 15,
            'TimeDiff': 0,
            'AmountDiff': 0
        }
        
        # Should not raise an exception
        result = preprocessor.transform_single(transaction)
        self.assertIsInstance(result, np.ndarray)
    
    def test_create_sequences(self):
        """Test create_sequences method."""
        preprocessor = Preprocessor(self.config_path)
        df_processed = preprocessor.fit_transform(self.sample_data.copy())
        
        # This won't create sequences with only 3 rows and lookback=10
        # But it should handle gracefully
        try:
            X_lstm, X_xgb, y = preprocessor.create_sequences(df_processed)
            # If sequences are created, check shapes
            if len(X_lstm) > 0:
                self.assertEqual(X_lstm.ndim, 3)  # 3D for LSTM
                self.assertEqual(X_xgb.ndim, 2)   # 2D for XGBoost
                self.assertEqual(y.ndim, 1)       # 1D for labels
        except ValueError:
            # Expected when data is too small
            pass
    
    def test_save_and_load_artifacts(self):
        """Test saving and loading artifacts."""
        import tempfile
        import shutil
        
        preprocessor = Preprocessor(self.config_path)
        preprocessor.fit_transform(self.sample_data.copy())
        
        # Create a temporary directory for artifacts
        temp_dir = tempfile.mkdtemp()
        original_artifacts_path = preprocessor.config['paths']['artifacts']
        
        try:
            # Temporarily change artifacts path
            preprocessor.config['paths']['artifacts'] = temp_dir
            
            # Save artifacts
            preprocessor.save_artifacts()
            
            # Check that files were created
            self.assertTrue(os.path.exists(os.path.join(temp_dir, 'label_encoders.pkl')))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, 'scaler.pkl')))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, 'feature_names.pkl')))
            
            # Create new preprocessor and load artifacts
            new_preprocessor = Preprocessor(self.config_path)
            new_preprocessor.config['paths']['artifacts'] = temp_dir
            new_preprocessor.load_artifacts()
            
            # Check that artifacts were loaded
            self.assertGreater(len(new_preprocessor.encoders), 0)
            self.assertGreater(len(new_preprocessor.scalers), 0)
            self.assertGreater(len(new_preprocessor.feature_names), 0)
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
