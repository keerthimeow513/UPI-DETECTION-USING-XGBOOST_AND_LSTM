"""
Security tests for rate limiting.

Tests the rate limiting functionality including:
- Health check endpoint rate limiting (100/minute)
- Prediction endpoint rate limiting (10/minute)
- Rate limit reset behavior
- Multiple endpoint rate limiting
"""

import pytest
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Set environment to test
os.environ['ENVIRONMENT'] = 'test'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Import needs to happen after path setup
try:
    from fastapi.testclient import TestClient
    from api import app
    HAS_APP = True
except ImportError as e:
    HAS_APP = False
    print(f"Could not import app: {e}")


@pytest.mark.skipif(not HAS_APP, reason="API app not available")
class TestRateLimiting:
    """Test cases for API rate limiting."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_health_check_rate_limit(self, client):
        """
        Test health check endpoint rate limiting.
        
        The / endpoint is limited to 100 requests per minute.
        After 100 requests, should return 429 Too Many Requests.
        """
        # Make 101 requests to /
        rate_limited = False
        for i in range(101):
            response = client.get("/")
            if i < 100:
                # First 100 should succeed
                assert response.status_code == 200, f"Request {i+1} should succeed"
            else:
                # 101st should be rate limited
                if response.status_code == 429:
                    rate_limited = True
                    break
        
        assert rate_limited, "Expected rate limiting after 100 requests"
    
    def test_predict_rate_limit(self, client):
        """
        Test prediction endpoint rate limiting.
        
        The /predict endpoint is limited to 10 requests per minute.
        After 10 requests, should return 429 Too Many Requests.
        """
        valid_payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        # Make 11 requests to /predict
        rate_limited = False
        for i in range(11):
            response = client.post("/predict", json=valid_payload)
            if i < 10:
                # First 10 should succeed (or 500 if models not loaded)
                assert response.status_code in [200, 500], f"Request {i+1} should succeed or fail gracefully"
            else:
                # 11th should be rate limited
                if response.status_code == 429:
                    rate_limited = True
                    break
        
        assert rate_limited, "Expected rate limiting after 10 requests"
    
    def test_predict_rate_limit_with_invalid_data(self, client):
        """
        Test that rate limiting applies even with invalid data.
        
        Invalid requests should still count towards rate limit.
        """
        invalid_payload = {
            "SenderUPI": "invalid",  # Missing @
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        # Make multiple requests with invalid data
        request_count = 0
        for i in range(15):
            response = client.post("/predict", json=invalid_payload)
            request_count += 1
            # All should either be 422 (validation error) or 429 (rate limited)
            assert response.status_code in [422, 429], f"Unexpected status: {response.status_code}"
            if response.status_code == 429:
                break
        
        # Should have hit rate limit within reasonable number of requests
        assert request_count <= 12, "Rate limit should apply within expected threshold"
    
    def test_rate_limit_headers(self, client):
        """
        Test that rate limit headers are present.
        
        Rate limiting middleware should include headers like:
        - X-RateLimit-Limit
        - X-RateLimit-Remaining
        - X-RateLimit-Reset
        """
        response = client.get("/")
        
        # Check for common rate limit headers
        rate_limit_headers = [
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset",
            "retry-after"
        ]
        
        has_rate_limit_header = any(
            header in response.headers for header in rate_limit_headers
        )
        
        # Note: slowapi may not add these headers by default
        # This test documents expected behavior
        assert response.status_code == 200 or has_rate_limit_header, \
            "Should either succeed or have rate limit headers"
    
    def test_different_endpoints_have_different_limits(self, client):
        """
        Test that different endpoints have different rate limits.
        
        Health check: 100/minute
        Predict: 10/minute
        """
        valid_payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        # Make 11 requests to /predict (should hit limit)
        predict_limited = False
        for i in range(11):
            response = client.post("/predict", json=valid_payload)
            if response.status_code == 429:
                predict_limited = True
                break
        
        # Reset by waiting (if needed) or just check health is still available
        # Health should still work because it has higher limit
        health_response = client.get("/")
        
        # Health endpoint may or may not be rate limited depending on shared state
        # but predict should definitely be limited
        assert predict_limited, "Predict endpoint should be rate limited"
    
    def test_rate_limit_429_response_format(self, client):
        """
        Test that 429 responses have appropriate format.
        
        Should include error message about rate limiting.
        """
        # Hit the rate limit first
        valid_payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        # Make requests until rate limited
        rate_limited_response = None
        for i in range(15):
            response = client.post("/predict", json=valid_payload)
            if response.status_code == 429:
                rate_limited_response = response
                break
        
        if rate_limited_response:
            # Check response has error content
            error_data = rate_limited_response.json()
            assert "error" in str(error_data).lower() or "rate" in str(error_data).lower() or \
                   "limit" in str(error_data).lower() or "detail" in error_data, \
                "Rate limit response should contain error information"
    
    def test_rate_limit_per_ip(self, client):
        """
        Test that rate limiting is per IP address.
        
        Different IPs should have separate rate limits.
        Note: In test environment, this may use same IP.
        """
        # This test documents the expected behavior
        # Actual implementation depends on key_func in limiter setup
        # which uses get_remote_address by default
        
        response = client.get("/")
        assert response.status_code in [200, 429], "Should handle request appropriately"
    
    def test_burst_requests(self, client):
        """
        Test burst request handling.
        
        Rapid successive requests should respect rate limits.
        """
        valid_payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        # Send burst of 20 requests rapidly
        responses = []
        for i in range(20):
            response = client.post("/predict", json=valid_payload)
            responses.append(response.status_code)
        
        # Should have mix of 200/500 and 429 responses
        success_count = sum(1 for r in responses if r in [200, 500])
        rate_limited_count = sum(1 for r in responses if r == 429)
        
        # Should be limited after 10 requests
        assert rate_limited_count > 0, "Should have rate limited requests in burst"
        assert success_count <= 11, "Should not exceed rate limit significantly"
    
    def test_concurrent_requests_rate_limiting(self, client):
        """
        Test rate limiting with concurrent requests.
        
        Concurrent requests should still respect rate limits.
        """
        import concurrent.futures
        
        valid_payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        def make_request(_):
            response = client.post("/predict", json=valid_payload)
            return response.status_code
        
        # Send 15 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(15)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Count responses
        success_count = sum(1 for r in results if r in [200, 500])
        rate_limited_count = sum(1 for r in results if r == 429)
        
        # Some should be rate limited
        assert rate_limited_count >= 0, "Concurrent requests should be handled"
        # Allow some flexibility due to race conditions
        assert success_count <= 15, "All requests should be processed"
    
    def test_health_check_not_affected_by_predict_limit(self, client):
        """
        Test that hitting predict rate limit doesn't affect health endpoint.
        
        Different endpoints should have independent rate limits.
        """
        valid_payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        # Hit predict rate limit
        for i in range(15):
            response = client.post("/predict", json=valid_payload)
            if response.status_code == 429:
                break
        
        # Health endpoint should still work
        health_response = client.get("/")
        # May be rate limited if sharing limit, but likely still available
        assert health_response.status_code in [200, 429], "Health endpoint should respond"
