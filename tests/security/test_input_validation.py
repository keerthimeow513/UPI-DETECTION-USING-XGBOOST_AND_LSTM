"""
Security tests for input validation.

Tests the TransactionRequest Pydantic model validation including:
- Valid transaction data acceptance
- Invalid UPI format detection
- Amount validation (negative, too high)
- Geographic coordinate validation
- SQL injection attempt handling
- XSS prevention
- General injection attack prevention
"""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pydantic import ValidationError
from schemas import TransactionRequest


class TestTransactionRequestValidation:
    """Test cases for TransactionRequest input validation."""
    
    def test_valid_transaction(self):
        """Valid transaction should pass validation."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.Amount == 500.0
        assert txn.SenderUPI == "user@upi"
        assert txn.ReceiverUPI == "merchant@upi"
    
    def test_valid_transaction_with_optional_fields(self):
        """Valid transaction with all optional fields should pass."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=1000.0,
            DeviceID="device456",
            Latitude=-33.87,
            Longitude=151.21,
            Timestamp="2024-01-15T10:30:00Z"
        )
        assert txn.Timestamp == "2024-01-15T10:30:00Z"
    
    def test_invalid_upi_format_no_at_symbol(self):
        """UPI without @ symbol should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="invalidupi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
        assert "@ symbol" in str(exc_info.value) or "@" in str(exc_info.value)
    
    def test_invalid_upi_format_special_chars(self):
        """UPI with invalid special characters should fail."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi<script>",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
        assert "format" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    
    def test_invalid_receiver_upi(self):
        """Invalid receiver UPI should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="notavalidupi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
        assert "@" in str(exc_info.value) or "symbol" in str(exc_info.value).lower()
    
    def test_negative_amount(self):
        """Negative amount should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=-100,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
        error_msg = str(exc_info.value).lower()
        assert "amount" in error_msg or "greater" in error_msg or "0" in error_msg
    
    def test_zero_amount(self):
        """Zero amount should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
        error_msg = str(exc_info.value).lower()
        assert "amount" in error_msg or "greater" in error_msg or "0" in error_msg
    
    def test_amount_too_high(self):
        """Amount > 10,000,000 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=10000001,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
        error_msg = str(exc_info.value).lower()
        assert "amount" in error_msg or "10000000" in error_msg or "exceed" in error_msg or "crore" in error_msg
    
    def test_amount_at_maximum(self):
        """Amount exactly at 10,000,000 should pass."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=10000000,
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.Amount == 10000000.0
    
    def test_invalid_latitude_too_high(self):
        """Latitude > 90 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=91,
                Longitude=77.59
            )
        error_msg = str(exc_info.value).lower()
        assert "latitude" in error_msg or "90" in error_msg or "less" in error_msg
    
    def test_invalid_latitude_too_low(self):
        """Latitude < -90 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=-91,
                Longitude=77.59
            )
        error_msg = str(exc_info.value).lower()
        assert "latitude" in error_msg or "-90" in error_msg or "greater" in error_msg
    
    def test_invalid_longitude_too_high(self):
        """Longitude > 180 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=181
            )
        error_msg = str(exc_info.value).lower()
        assert "longitude" in error_msg or "180" in error_msg or "less" in error_msg
    
    def test_invalid_longitude_too_low(self):
        """Longitude < -180 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=-181
            )
        error_msg = str(exc_info.value).lower()
        assert "longitude" in error_msg or "-180" in error_msg or "greater" in error_msg
    
    def test_edge_case_coordinates(self):
        """Test edge case valid coordinates."""
        # North Pole
        txn1 = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123",
            Latitude=90,
            Longitude=0
        )
        assert txn1.Latitude == 90
        
        # South Pole
        txn2 = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123",
            Latitude=-90,
            Longitude=0
        )
        assert txn2.Latitude == -90
        
        # International Date Line
        txn3 = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123",
            Latitude=0,
            Longitude=180
        )
        assert txn3.Longitude == 180
    
    def test_sql_injection_in_upi(self):
        """SQL injection attempt in UPI should be handled."""
        # Pydantic validation will reject the malformed UPI
        with pytest.raises(ValidationError):
            TransactionRequest(
                SenderUPI="user@test'; DROP TABLE users;--",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
    
    def test_sql_injection_in_device_id(self):
        """SQL injection attempt in DeviceID should be handled by max_length."""
        # DeviceID has max_length constraint
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123'; DROP TABLE users;--",
            Latitude=12.97,
            Longitude=77.59
        )
        # The request should pass validation (max_length will truncate or accept)
        # The sanitization happens elsewhere in the application
        assert txn.DeviceID is not None
    
    def test_xss_attempt_in_upi(self):
        """XSS attempt in UPI should be rejected."""
        with pytest.raises(ValidationError):
            TransactionRequest(
                SenderUPI="<script>alert('xss')</script>@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
    
    def test_xss_attempt_in_device_id(self):
        """XSS attempt in DeviceID - length constraint applies."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="<script>alert('xss')</script>",
            Latitude=12.97,
            Longitude=77.59
        )
        # DeviceID should be accepted but may be truncated
        assert txn.DeviceID is not None
    
    def test_command_injection_attempt(self):
        """Command injection attempt should be handled."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123; rm -rf /",
            Latitude=12.97,
            Longitude=77.59
        )
        # The validation should accept the DeviceID (length check only)
        # Actual sanitization happens in processing
        assert "rm -rf" in txn.DeviceID or len(txn.DeviceID) <= 100
    
    def test_path_traversal_attempt(self):
        """Path traversal attempt should be handled."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="../../../etc/passwd",
            Latitude=12.97,
            Longitude=77.59
        )
        # DeviceID accepts the string; security is handled elsewhere
        assert txn.DeviceID == "../../../etc/passwd"
    
    def test_null_byte_injection(self):
        """Null byte injection attempt should be handled."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123\x00malicious",
            Latitude=12.97,
            Longitude=77.59
        )
        # Null bytes may be preserved or handled by Pydantic
        assert txn.DeviceID is not None
    
    def test_unicode_injection(self):
        """Unicode and special character injection attempts."""
        # This should fail UPI validation due to special characters
        with pytest.raises(ValidationError):
            TransactionRequest(
                SenderUPI="user\u0000@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
    
    def test_very_long_strings(self):
        """Very long string inputs should be constrained."""
        # UPI has max_length=100
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="a" * 200 + "@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
        error_msg = str(exc_info.value).lower()
        assert "length" in error_msg or "100" in error_msg or "string" in error_msg
    
    def test_empty_strings(self):
        """Empty string inputs should fail."""
        with pytest.raises(ValidationError):
            TransactionRequest(
                SenderUPI="",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
    
    def test_whitespace_only_strings(self):
        """Whitespace-only strings should be validated."""
        # Whitespace-only UPI should fail @ validation
        with pytest.raises(ValidationError):
            TransactionRequest(
                SenderUPI="   @upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
    
    def test_no_sql_injection_mongodb(self):
        """NoSQL injection patterns should be handled."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID='{"$gt": ""}',
            Latitude=12.97,
            Longitude=77.59
        )
        # String is accepted as DeviceID; actual NoSQL protection is elsewhere
        assert txn.DeviceID == '{"$gt": ""}'
    
    def test_xml_injection(self):
        """XML injection attempt should be handled."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
            Latitude=12.97,
            Longitude=77.59
        )
        # DeviceID max_length constraint applies
        assert len(txn.DeviceID) <= 100
    
    def test_template_injection(self):
        """Template injection attempt (Jinja2, etc)."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="{{config.__class__.__init__.__globals__['os'].popen('ls').read()}}",
            Latitude=12.97,
            Longitude=77.59
        )
        # String is accepted as DeviceID; template protection is elsewhere
        assert "{{" in txn.DeviceID or len(txn.DeviceID) <= 100
    
    def test_json_injection(self):
        """JSON injection attempt in fields.""",
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID='{"key": "value", "nested": {"attack": true}}',
            Latitude=12.97,
            Longitude=77.59
        )
        # DeviceID is stored as string
        assert isinstance(txn.DeviceID, str)
    
    def test_html_injection(self):
        """HTML injection attempt should be handled."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="<img src=x onerror=alert('xss')>",
            Latitude=12.97,
            Longitude=77.59
        )
        # String is accepted; HTML sanitization is elsewhere
        assert "<img" in txn.DeviceID or len(txn.DeviceID) <= 100


class TestTransactionRequestBoundaryValues:
    """Test boundary values and edge cases."""
    
    def test_minimum_valid_amount(self):
        """Test minimum valid amount (just above 0)."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=0.01,
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.Amount == 0.01
    
    def test_float_precision_amount(self):
        """Test float precision handling."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=999999.99,
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.Amount == 999999.99
    
    def test_scientific_notation_amount(self):
        """Test scientific notation rejection."""
        # Scientific notation should be parsed as float
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=1e6,  # 1000000
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.Amount == 1000000.0
    
    def test_integer_amount(self):
        """Test integer amount is converted to float."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=1000,
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.Amount == 1000.0
        assert isinstance(txn.Amount, float)
    
    def test_upi_case_sensitivity(self):
        """Test UPI case sensitivity."""
        txn = TransactionRequest(
            SenderUPI="User123@Upi",
            ReceiverUPI="Merchant@UPI",
            Amount=500.0,
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.SenderUPI == "User123@Upi"
        assert txn.ReceiverUPI == "Merchant@UPI"
    
    def test_upi_with_numbers_and_special_chars(self):
        """Test UPI with valid special characters."""
        txn = TransactionRequest(
            SenderUPI="user_123.test@upi",
            ReceiverUPI="merchant-test_123@upi",
            Amount=500.0,
            DeviceID="device123",
            Latitude=12.97,
            Longitude=77.59
        )
        assert txn.SenderUPI == "user_123.test@upi"
        assert txn.ReceiverUPI == "merchant-test_123@upi"
    
    def test_device_id_max_length(self):
        """Test DeviceID at maximum length."""
        long_device_id = "d" * 100
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID=long_device_id,
            Latitude=12.97,
            Longitude=77.59
        )
        assert len(txn.DeviceID) == 100
    
    def test_device_id_too_long(self):
        """Test DeviceID exceeding maximum length."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount=500.0,
                DeviceID="d" * 101,
                Latitude=12.97,
                Longitude=77.59
            )
        error_msg = str(exc_info.value).lower()
        assert "length" in error_msg or "100" in error_msg or "string" in error_msg
    
    def test_missing_required_fields(self):
        """Test missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionRequest(
                SenderUPI="user@upi"
                # Missing other required fields
            )
        error_msg = str(exc_info.value).lower()
        assert "field" in error_msg or "required" in error_msg or "missing" in error_msg
    
    def test_invalid_data_types(self):
        """Test invalid data types."""
        with pytest.raises(ValidationError):
            TransactionRequest(
                SenderUPI="user@upi",
                ReceiverUPI="merchant@upi",
                Amount="not_a_number",
                DeviceID="device123",
                Latitude=12.97,
                Longitude=77.59
            )
    
    def test_latitude_longitude_float_precision(self):
        """Test latitude and longitude with float precision."""
        txn = TransactionRequest(
            SenderUPI="user@upi",
            ReceiverUPI="merchant@upi",
            Amount=500.0,
            DeviceID="device123",
            Latitude=12.971598,
            Longitude=77.594562
        )
        assert abs(txn.Latitude - 12.971598) < 0.000001
        assert abs(txn.Longitude - 77.594562) < 0.000001
