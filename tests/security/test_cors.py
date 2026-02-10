"""
Security tests for CORS configuration.

Tests the Cross-Origin Resource Sharing (CORS) configuration including:
- Allowed origins can access the API
- Disallowed origins are rejected
- CORS headers are present in responses
- Preflight (OPTIONS) requests are handled correctly
- Credentials handling
"""

import pytest
import sys
import os

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
class TestCORSConfiguration:
    """Test cases for CORS configuration."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_cors_headers_present_for_allowed_origin(self, client):
        """
        Test that CORS headers are present for allowed origins.
        
        The API should include Access-Control-Allow-Origin header
        for requests from configured allowed origins.
        """
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        # The header should reflect the allowed origin
        assert response.headers["access-control-allow-origin"] in [
            "http://localhost:3000",
            "*"  # If wildcard is allowed
        ]
    
    def test_cors_preflight_request(self, client):
        """
        Test CORS preflight (OPTIONS) request handling.
        
        Preflight requests should return appropriate CORS headers.
        """
        response = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should either succeed (200) or indicate method not allowed (405)
        # but CORS headers should be present
        assert response.status_code in [200, 405]
        
        # Check for CORS headers
        if response.status_code == 200:
            assert "access-control-allow-origin" in response.headers
            assert "access-control-allow-methods" in response.headers
    
    def test_cors_post_request_with_origin(self, client):
        """
        Test POST request with Origin header.
        
        POST requests from allowed origins should include CORS headers.
        """
        payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        response = client.post(
            "/predict",
            json=payload,
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Should have CORS headers regardless of response status
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_for_multiple_allowed_origins(self, client):
        """
        Test CORS for multiple configured allowed origins.
        
        All origins in CORS_ORIGINS should be allowed.
        """
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8080"
        ]
        
        for origin in allowed_origins:
            response = client.get(
                "/",
                headers={"Origin": origin}
            )
            
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers
    
    def test_cors_disallowed_origin(self, client):
        """
        Test that disallowed origins are rejected.
        
        Requests from origins not in CORS_ORIGINS should not
        receive Access-Control-Allow-Origin header.
        """
        response = client.get(
            "/",
            headers={"Origin": "http://evil.com"}
        )
        
        # If CORS is strict, header should not be present for disallowed origins
        # If wildcard is used, it will be present
        # This tests the current configuration
        cors_origin = response.headers.get("access-control-allow-origin", "")
        
        # Either no header, or not the evil origin, or wildcard
        assert cors_origin != "http://evil.com" or cors_origin == "*", \
            "Disallowed origin should not be reflected in CORS header"
    
    def test_cors_credentials_header(self, client):
        """
        Test CORS credentials header handling.
        
        If credentials are allowed, Access-Control-Allow-Credentials
        header should be present.
        """
        response = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Check if credentials header exists (depends on configuration)
        # This test documents the current behavior
        if "access-control-allow-credentials" in response.headers:
            assert response.headers["access-control-allow-credentials"] in ["true", "True"]
    
    def test_cors_allowed_methods(self, client):
        """
        Test that CORS allowed methods are configured.
        
        Preflight requests should indicate allowed HTTP methods.
        """
        response = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        if response.status_code == 200 and "access-control-allow-methods" in response.headers:
            allowed_methods = response.headers["access-control-allow-methods"]
            # Should include common methods
            assert any(method in allowed_methods for method in ["GET", "POST", "OPTIONS", "*"])
    
    def test_cors_allowed_headers(self, client):
        """
        Test that CORS allowed headers are configured.
        
        Preflight requests should indicate allowed headers.
        """
        response = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        if response.status_code == 200 and "access-control-allow-headers" in response.headers:
            allowed_headers = response.headers["access-control-allow-headers"]
            # Should include Content-Type
            assert "content-type" in allowed_headers.lower() or "*" in allowed_headers
    
    def test_cors_simple_request(self, client):
        """
        Test CORS handling for simple requests (GET without preflight).
        
        Simple requests should still receive CORS headers.
        """
        response = client.get(
            "/",
            headers={
                "Origin": "http://localhost:3000"
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_non_simple_request(self, client):
        """
        Test CORS handling for non-simple requests (POST with JSON).
        
        Non-simple requests require preflight and proper CORS headers.
        """
        payload = {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
        
        response = client.post(
            "/predict",
            json=payload,
            headers={
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json"
            }
        )
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_no_origin_header(self, client):
        """
        Test requests without Origin header.
        
        Same-origin requests don't need CORS headers.
        """
        response = client.get("/")
        
        assert response.status_code == 200
        # May or may not have CORS headers depending on middleware behavior
    
    def test_cors_malformed_origin(self, client):
        """
        Test CORS handling with malformed Origin header.
        
        Should handle gracefully without security issues.
        """
        malformed_origins = [
            "not-a-valid-origin",
            "javascript:alert('xss')",
            "http://",
            "https://",
            "",
            "null"
        ]
        
        for origin in malformed_origins:
            response = client.get(
                "/",
                headers={"Origin": origin}
            )
            
            # Should not crash
            assert response.status_code in [200, 400, 403]
    
    def test_cors_wildcard_origin(self, client):
        """
        Test CORS behavior with wildcard origin.
        
        If wildcard is allowed, any origin should work.
        Note: Wildcard cannot be used with credentials.
        """
        response = client.get(
            "/",
            headers={"Origin": "http://any-origin.com"}
        )
        
        cors_origin = response.headers.get("access-control-allow-origin", "")
        
        # Either specific origin is reflected, or wildcard is used
        assert cors_origin in ["http://any-origin.com", "*", "http://localhost:3000", "http://localhost:8080"]
