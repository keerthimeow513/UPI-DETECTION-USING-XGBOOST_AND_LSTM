import unittest # Import the standard Python unit testing framework
import os # Import OS library for checking file and directory existence
import sys # Import system library for path manipulation
import json # Import json for potential data verification
import numpy as np # Import numpy for numerical assertions if needed

# Add the project root directory to sys.path so the test runner can find the 'utils' and '04_inference' modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable GPU usage for tests to ensure they run quickly and consistently on any machine
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class TestProjectStructure(unittest.TestCase): # Define a test class containing suite of project integrity tests
    
    def test_directory_structure(self): # Test case to ensure all professional folder structures are intact
        """Verify the professional directory structure exists."""
        required_dirs = [ # List of folders that must exist for the project to function correctly
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
        for d in required_dirs: # Loop through each required directory
            # Assert that the path exists; if not, raise an error with a descriptive message
            self.assertTrue(os.path.exists(d), f"Directory {d} missing")

    def test_imports(self): # Test case to verify that the core utility modules are bug-free and importable
        """Test if modules can be imported without syntax errors."""
        try: # Try-except block to catch and report import failures
            from utils.preprocessing import Preprocessor # Attempt to import the Preprocessor class
            from utils.logger import setup_logger # Attempt to import the logger setup function
        except ImportError as e: # If the import fails...
            self.fail(f"Failed to import utilities: {e}") # ...mark the test as failed

    def test_api_logic(self): # Test case to verify the actual AI prediction logic works end-to-end
        """Test the inference service logic (mocking the API call)."""
        # We need to simulate the service initialization
        # This requires the models to be present; we check for the XGBoost model as a proxy
        if not os.path.exists('02_models/artifacts/xgb_model.pkl'):
            print("Skipping inference test - models not trained yet")
            return # Skip test gracefully if training hasn't occurred

        try: # Try to initialize the service and run a sample prediction
            sys.path.append('04_inference') # Add inference folder to path for local imports within service.py
            from service import FraudDetectionService # Import the core AI service
            service = FraudDetectionService('07_configs/config.yaml') # Initialize service with the config file
            
            # Create a sample transaction payload (dummy data)
            payload = {
                "SenderUPI": "test@upi",
                "ReceiverUPI": "shop@upi",
                "Amount": 500.0,
                "DeviceID": "mac_addr",
                "Latitude": 12.0,
                "Longitude": 77.0
            }
            
            result = service.predict(payload) # Run the sample payload through the AI prediction pipeline
            self.assertIn('risk_score', result) # Assert that the output contains a risk score
            self.assertIn('verdict', result) # Assert that the output contains a final verdict (ALLOW/FLAG/BLOCK)
            print("\nInference Logic: PASS") # Print a success message to the console
            
        except Exception as e: # Catch any runtime errors during the prediction test
            self.fail(f"Inference service failed: {e}") # Mark the test as failed

if __name__ == '__main__': # Entry point for running the tests directly
    unittest.main() # Run all defined test cases
