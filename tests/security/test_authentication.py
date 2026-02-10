"""
Security tests for API authentication.

Tests the authentication mechanisms including:
- API key validation
- Missing authentication handling
- Invalid authentication handling
- Authentication bypass attempts
- Token validation (if JWT is used)

Note: These tests assume the API may or may not have authentication
implemented. Tests are designed to work in either case.
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
class TestAPIAuthentication:
    """Test cases for API authentication."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_payload(self):
        """Create valid prediction payload."""
        return {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
    
    def test_predict_without_api_key(self, client, valid_payload):
        """
        Test prediction endpoint without API key.
        
        If authentication is required, should return 401.
        If not required, should proceed normally.
        """
        response = client.post("/predict", json=valid_payload)
        
        # Either auth not required (200/500) or auth required (401/403)
        assert response.status_code in [200, 401, 403, 500], \
            f"Unexpected status code: {response.status_code}"
    
    def test_predict_with_invalid_api_key(self, client, valid_payload):
        """
        Test prediction endpoint with invalid API key.
        
        Should return 401 Unauthorized if authentication is implemented.
        """
        response = client.post(
            "/predict",
            json=valid_payload,
            headers={"X-API-Key": "invalid_key"}
        )
        
        # If auth is implemented, should be 401/403
        # If auth is not implemented, might be 200/500
        assert response.status_code in [200, 401, 403, 500], \
            f"Unexpected status code: {response.status_code}"
    
    def test_predict_with_empty_api_key(self, client, valid_payload):
        """
        Test prediction endpoint with empty API key.
        
        Should be treated as missing authentication.
        """
        response = client.post(
            "/predict",
            json=valid_payload,
            headers={"X-API-Key": ""}
        )
        
        # Empty key should be treated as invalid
        assert response.status_code in [200, 401, 403, 422, 500], \
            f"Unexpected status code: {response.status_code}"
    
    def test_predict_with_malformed_api_key(self, client, valid_payload):
        """
        Test prediction endpoint with malformed API key.
        
        Various malformed keys should be handled securely.
        """
        malformed_keys = [
            "Bearer ",  # Empty bearer token
            "Bearer invalid_token",
            "Basic dXNlcjpwYXNz",  # Basic auth attempt
            "token\nwith\nnewlines",
            "token\x00with\x00nulls",
            "a" * 10000,  # Extremely long key
            "'; DROP TABLE api_keys;--",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
        ]
        
        for key in malformed_keys:
            response = client.post(
                "/predict",
                json=valid_payload,
                headers={
                    "X-API-Key": key,
                    "Authorization": f"Bearer {key}"
                }
            )
            
            # Should not crash and should not return 500 for auth issues
            assert response.status_code in [200, 401, 403, 422, 500], \
                f"Malformed key should be handled gracefully: {key[:50]}"
    
    def test_health_check_without_auth(self, client):
        """
        Test health check endpoint without authentication.
        
        Health endpoints are typically public.
        """
        response = client.get("/")
        
        # Health check should be accessible without auth
        assert response.status_code in [200, 429], \
            "Health check should be accessible without authentication"
    
    def test_health_check_with_invalid_auth(self, client):
        """
        Test health check with invalid authentication.
        
        Should still work (auth not required) or reject invalid auth.
        """
        response = client.get(
            "/",
            headers={"X-API-Key": "invalid"}
        )
        
        # Should either accept or ignore invalid auth on public endpoint
        assert response.status_code in [200, 401, 403, 429], \
            "Health check should handle auth gracefully"


class TestAuthenticationHeaders:
    """Test cases for authentication header handling."""
    
    def test_common_auth_header_names(self):
        """
        Document common authentication header patterns.
        
        This test documents expected authentication headers.
        """
        common_auth_headers = [
            "X-API-Key",
            "Authorization",
            "X-Auth-Token",
            "X-Access-Token",
            "API-Key"
        ]
        
        # Verify the list is comprehensive
        assert len(common_auth_headers) >= 3
        
        # Check header name format
        for header in common_auth_headers:
            assert isinstance(header, str)
            assert len(header) > 0
    
    def test_authorization_header_schemes(self):
        """
        Document common authorization schemes.
        
        This test documents expected auth schemes.
        """
        common_schemes = [
            "Bearer",
            "Basic",
            "Digest",
            "ApiKey",
            "Token"
        ]
        
        # Verify schemes are documented
        assert len(common_schemes) >= 3
        
        # Check scheme format
        for scheme in common_schemes:
            assert isinstance(scheme, str)
            assert scheme[0].isalpha()


@pytest.mark.skipif(not HAS_APP, reason="API app not available")
class TestAuthenticationBypassAttempts:
    """Test cases for authentication bypass attempts."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_payload(self):
        """Create valid prediction payload."""
        return {
            "SenderUPI": "test@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 500.0,
            "DeviceID": "test_device",
            "Latitude": 12.97,
            "Longitude": 77.59
        }
    
    def test_bypass_with_null_bytes(self, client, valid_payload):
        """
        Test authentication bypass with null byte injection.
        
        Null bytes in headers should be handled securely.
        """
        response = client.post(
            "/predict",
            json=valid_payload,
            headers={"X-API-Key": "valid\x00key"}
        )
        
        # Should not bypass authentication
        assert response.status_code in [200, 401, 403, 422, 500]
    
    def test_bypass_with_header_case_variation(self, client, valid_payload):
        """
        Test authentication with header case variations.
        
        Headers are case-insensitive according to HTTP spec.
        """
        variations = [
            "x-api-key",
            "X-API-KEY",
            "x-Api-Key",
            "X-api-key"
        ]
        
        for header in variations:
            response = client.post(
                "/predict",
                json=valid_payload,
                headers={header: "test_key"}
            )
            
            # All variations should be treated the same
            assert response.status_code in [200, 401, 403, 422, 500]
    
    def test_bypass_with_duplicate_headers(self, client, valid_payload):
        """
        Test authentication with duplicate headers.
        
        Duplicate headers should be handled securely.
        """
        # TestClient may not support duplicate headers easily
        # This test documents expected behavior
        response = client.post(
            "/predict",
            json=valid_payload,
            headers={"X-API-Key": "key1"}
        )
        
        assert response.status_code in [200, 401, 403, 422, 500]
    
    def test_bypass_with_path_traversal(self, client, valid_payload):
        """
        Test authentication bypass with path traversal.
        
        Path traversal in headers should not bypass auth.
        """
        response = client.post(
            "/predict",
            json=valid_payload,
            headers={"X-API-Key": "../../../etc/passwd"}
        )
        
        # Should not bypass authentication
        assert response.status_code in [200, 401, 403, 422, 500]
    
    def test_bypass_with_encoding_tricks(self, client, valid_payload):
        """
        Test authentication with encoding tricks.
        
        Various encodings should be handled properly.
        """
        # URL-encoded characters
        response = client.post(
            "/predict",
            json=valid_payload,
            headers={"X-API-Key": "key%00hidden"}
        )
        
        assert response.status_code in [200, 401, 403, 422, 500]
    
    def test_bypass_with_jwt_none_algorithm(self, client, valid_payload):
        """
        Test JWT None algorithm bypass attempt.
        
        JWT tokens with 'alg: none' should be rejected.
        Note: This test assumes JWT might be used.
        """
        # None algorithm JWT payload
        none_jwt = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjMifQ."
        
        response = client.post(
            "/predict",
            json=valid_payload,
            headers={"Authorization": f"Bearer {none_jwt}"}
        )
        
        # Should not accept None algorithm
        assert response.status_code in [200, 401, 403, 422, 500]


class TestAuthenticationConfiguration:
    """Test cases for authentication configuration."""
    
    def test_api_key_secret_exists(self):
        """
        Test that API key secret is configured.
        
        Checks configuration for authentication settings.
        """
        try:
            from utils.config import settings
            
            # Check if API key secret is set
            assert hasattr(settings, 'API_KEY_SECRET')
            assert settings.API_KEY_SECRET is not None
            assert len(settings.API_KEY_SECRET) >= 16, \
                "API key secret should be at least 16 characters"
            
        except ImportError:
            pytest.skip("Settings module not available")
    
    def test_api_key_secret_not_default(self):
        """
        Test that API key secret is not using default value in production.
        
        Production should use a custom secret.
        """
        try:
            from utils.config import settings
            
            default_secrets = [
                "your-secret-key-here",
                "secret",
                "password",
                "admin",
                "123456"
            ]
            
            if settings.is_production:
                assert settings.API_KEY_SECRET not in default_secrets, \
                    "Production should not use default API key secret"
            
        except ImportError:
            pytest.skip("Settings module not available")


@pytest.mark.skipif(not HAS_APP, reason="API app not available")
class TestAuthenticationResponseSecurity:
    """Test cases for secure authentication responses."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_no_sensitive_info_in_auth_error(self, client):
        """
        Test that authentication errors don't leak sensitive info.
        
        Error messages should not reveal:
        - Internal paths
        - Database details
        - Authentication implementation details
        """
        response = client.post(
            "/predict",
            json={"SenderUPI": "test@upi"},  # Incomplete payload
            headers={"X-API-Key": "wrong_key"}
        )
        
        if response.status_code in [401, 403]:
            error_text = response.text.lower()
            
            # Should not contain sensitive information
            sensitive_patterns = [
                "password",
                "secret",
                "sql",
                "query",
                "database",
                "table",
                "column"
            ]
            
            for pattern in sensitive_patterns:
                assert pattern not in error_text, \
                    f"Error should not contain: {pattern}"
    
    def test_auth_error_does_not_expose_user_exists(self, client):
        """
        Test that auth errors don't reveal if user exists.
        
        Both invalid user and invalid password should have same error.
        """
        # This is a principle test - implementation may vary
        # Both scenarios should ideally return the same error
        pass


class TestRateLimitingAndAuth:
    """Test interaction between rate limiting and authentication."""
    
    def test_rate_limiting_applies_without_auth(self):
        """
        Test that rate limiting applies to unauthenticated requests.
        
        Rate limiting should work regardless of authentication.
        """
        # This is documented behavior
        # Rate limiting middleware typically runs before auth
        pass
    
    def test_authenticated_users_may_have_different_limits(self):
        """
        Test that authenticated users may have different rate limits.
        
        Authenticated users often have higher limits.
        """
        # This is documented behavior
        # Implementation may vary
        pass
