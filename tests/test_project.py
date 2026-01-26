import unittest
import os
import sys
import json
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class TestProjectStructure(unittest.TestCase):
    
    def test_directory_structure(self):
        """Verify the professional directory structure exists."""
        required_dirs = [
            '01_data/raw',
            '01_data/processed',
            '02_models/artifacts',
            '03_training',
            '04_inference',
            'utils',
            '06_dashboard',
            '06_notebooks',
            '07_configs'
        ]
        for d in required_dirs:
            self.assertTrue(os.path.exists(d), f"Directory {d} missing")

    def test_imports(self):
        """Test if modules can be imported without syntax errors."""
        try:
            from utils.preprocessing import Preprocessor
            from utils.logger import setup_logger
        except ImportError as e:
            self.fail(f"Failed to import utilities: {e}")

    def test_api_logic(self):
        """Test the inference service logic (mocking the API call)."""
        # We need to simulate the service initialization
        # This requires the models to be present
        if not os.path.exists('02_models/artifacts/xgb_model.pkl'):
            print("Skipping inference test - models not trained yet")
            return

        try:
            sys.path.append('04_inference')
            from service import FraudDetectionService
            service = FraudDetectionService('07_configs/config.yaml')
            
            # Dummy payload
            payload = {
                "SenderUPI": "test@upi",
                "ReceiverUPI": "shop@upi",
                "Amount": 500.0,
                "DeviceID": "mac_addr",
                "Latitude": 12.0,
                "Longitude": 77.0
            }
            
            result = service.predict(payload)
            self.assertIn('risk_score', result)
            self.assertIn('verdict', result)
            print("\nInference Logic: PASS")
            
        except Exception as e:
            self.fail(f"Inference service failed: {e}")

if __name__ == '__main__':
    unittest.main()
