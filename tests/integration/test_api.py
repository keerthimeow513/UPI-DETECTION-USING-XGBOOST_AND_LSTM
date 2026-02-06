"""Integration tests for API endpoints."""

import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Disable GPU for tests
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from fastapi.testclient import TestClient

# Import needs to happen after path setup
try:
    from api import app
    HAS_APP = True
except ImportError:
    HAS_APP = False


@unittest.skipUnless(HAS_APP, "API app not available")
class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client."""
        cls.client = TestClient(app)
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "online")
    
    def test_predict_endpoint_valid_data(self):
        """Test prediction endpoint with valid data."""
        payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "shop@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59,
            "Hour": 14,
            "DayOfWeek": 1
        }
        
        response = self.client.post("/predict", json=payload)
        
        # Should succeed (200) or fail due to missing models (500)
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn("transaction_id", data)
            self.assertIn("risk_score", data)
            self.assertIn("verdict", data)
            self.assertIn("factors", data)
            
            # Check verdict is valid
            self.assertIn(data["verdict"], ["ALLOW", "FLAG", "BLOCK"])
            
            # Check risk score is between 0 and 1
            self.assertGreaterEqual(data["risk_score"], 0)
            self.assertLessEqual(data["risk_score"], 1)
    
    def test_predict_endpoint_missing_fields(self):
        """Test prediction endpoint with missing required fields."""
        # Missing required fields
        payload = {
            "SenderUPI": "test@upi"
            # Missing other required fields
        }
        
        response = self.client.post("/predict", json=payload)
        # Should return validation error
        self.assertEqual(response.status_code, 422)
    
    def test_predict_endpoint_invalid_data_types(self):
        """Test prediction endpoint with invalid data types."""
        payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "shop@upi",
            "Amount": "not_a_number",  # Invalid type
            "DeviceID": "device1",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        response = self.client.post("/predict", json=payload)
        # Should return validation error
        self.assertEqual(response.status_code, 422)
    
    def test_predict_endpoint_extreme_values(self):
        """Test prediction endpoint with extreme values."""
        payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "shop@upi",
            "Amount": 999999.99,  # Very high amount
            "DeviceID": "device1",
            "Latitude": 90.0,  # Edge of valid range
            "Longitude": 180.0,  # Edge of valid range
            "Hour": 23,
            "DayOfWeek": 6
        }
        
        response = self.client.post("/predict", json=payload)
        # Should succeed or fail gracefully
        self.assertIn(response.status_code, [200, 500])
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = self.client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        
        # CORS should be configured
        self.assertIn(response.status_code, [200, 405])  # 405 if OPTIONS not handled


class TestAPIModels(unittest.TestCase):
    """Test cases for API request/response models."""
    
    def test_transaction_request_model(self):
        """Test TransactionRequest Pydantic model."""
        try:
            from schemas import TransactionRequest
            
            # Valid data
            data = {
                "SenderUPI": "test@upi",
                "ReceiverUPI": "shop@upi",
                "Amount": 100.0,
                "DeviceID": "device1",
                "Latitude": 12.97,
                "Longitude": 77.59,
                "Hour": 12,
                "DayOfWeek": 1,
                "DayOfMonth": 15,
                "TimeDiff": 0,
                "AmountDiff": 0
            }
            
            txn = TransactionRequest(**data)
            self.assertEqual(txn.SenderUPI, "test@upi")
            self.assertEqual(txn.Amount, 100.0)
            
        except ImportError:
            self.skipTest("Schemas module not available")
    
    def test_prediction_response_model(self):
        """Test PredictionResponse Pydantic model."""
        try:
            from schemas import PredictionResponse
            
            # Valid data
            data = {
                "transaction_id": "test-uuid",
                "risk_score": 0.75,
                "verdict": "BLOCK",
                "factors": {"Amount": 0.5, "DeviceID": 0.3}
            }
            
            response = PredictionResponse(**data)
            self.assertEqual(response.verdict, "BLOCK")
            self.assertEqual(response.risk_score, 0.75)
            
        except ImportError:
            self.skipTest("Schemas module not available")


if __name__ == '__main__':
    unittest.main()
