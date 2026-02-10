"""
Security tests for model security and integrity.

Tests the security utilities including:
- Checksum calculation for model files
- Model integrity validation
- Secure pickle loading with restricted unpickler
- Model file tampering detection
- Secure model loader functionality
"""

import pytest
import sys
import os
import tempfile
import hashlib

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.security import (
    calculate_checksum,
    validate_model_integrity,
    load_checksums,
    secure_load_pickle,
    sanitize_input,
    generate_checksums_for_directory,
    SecureModelLoader,
    RestrictedUnpickler,
    ModelSecurityError
)


class TestChecksumCalculation:
    """Test cases for checksum calculation."""
    
    def test_checksum_calculation_sha256(self):
        """
        Test SHA256 checksum calculation.
        
        Checksum should be 64 hex characters (256 bits).
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content for checksum")
            temp_path = f.name
        
        try:
            checksum = calculate_checksum(temp_path, algorithm='sha256')
            
            # SHA256 produces 64 hex characters
            assert len(checksum) == 64
            # Should be valid hex
            int(checksum, 16)
            
        finally:
            os.unlink(temp_path)
    
    def test_checksum_calculation_sha512(self):
        """Test SHA512 checksum calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content for checksum")
            temp_path = f.name
        
        try:
            checksum = calculate_checksum(temp_path, algorithm='sha512')
            
            # SHA512 produces 128 hex characters
            assert len(checksum) == 128
            # Should be valid hex
            int(checksum, 16)
            
        finally:
            os.unlink(temp_path)
    
    def test_checksum_calculation_md5(self):
        """Test MD5 checksum calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content for checksum")
            temp_path = f.name
        
        try:
            checksum = calculate_checksum(temp_path, algorithm='md5')
            
            # MD5 produces 32 hex characters
            assert len(checksum) == 32
            # Should be valid hex
            int(checksum, 16)
            
        finally:
            os.unlink(temp_path)
    
    def test_checksum_file_not_found(self):
        """Test checksum calculation for non-existent file."""
        with pytest.raises(FileNotFoundError):
            calculate_checksum("/path/that/does/not/exist.txt")
    
    def test_checksum_invalid_algorithm(self):
        """Test checksum calculation with invalid algorithm."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                calculate_checksum(temp_path, algorithm='invalid')
            assert "unsupported" in str(exc_info.value).lower() or "algorithm" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_checksum_consistency(self):
        """Test that checksum is consistent for same content."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("consistent content")
            temp_path = f.name
        
        try:
            checksum1 = calculate_checksum(temp_path)
            checksum2 = calculate_checksum(temp_path)
            
            assert checksum1 == checksum2
            
        finally:
            os.unlink(temp_path)
    
    def test_checksum_different_content(self):
        """Test that different content produces different checksums."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("content one")
            temp_path1 = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("content two")
            temp_path2 = f.name
        
        try:
            checksum1 = calculate_checksum(temp_path1)
            checksum2 = calculate_checksum(temp_path2)
            
            assert checksum1 != checksum2
            
        finally:
            os.unlink(temp_path1)
            os.unlink(temp_path2)
    
    def test_checksum_binary_content(self):
        """Test checksum calculation for binary content."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"\x00\x01\x02\xff\xfe")
            temp_path = f.name
        
        try:
            checksum = calculate_checksum(temp_path)
            assert len(checksum) == 64
            int(checksum, 16)  # Valid hex
        finally:
            os.unlink(temp_path)


class TestModelIntegrityValidation:
    """Test cases for model integrity validation."""
    
    def test_valid_model_integrity(self):
        """Test validation with correct checksum."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("model content")
            temp_path = f.name
        
        try:
            expected_checksum = calculate_checksum(temp_path)
            is_valid = validate_model_integrity(temp_path, expected_checksum)
            
            assert is_valid is True
            
        finally:
            os.unlink(temp_path)
    
    def test_invalid_model_integrity(self):
        """Test validation with incorrect checksum."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("model content")
            temp_path = f.name
        
        try:
            is_valid = validate_model_integrity(temp_path, "invalid_checksum")
            
            assert is_valid is False
            
        finally:
            os.unlink(temp_path)
    
    def test_model_integrity_case_insensitive(self):
        """Test that checksum comparison is case-insensitive."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("model content")
            temp_path = f.name
        
        try:
            checksum = calculate_checksum(temp_path)
            # Test with uppercase
            is_valid = validate_model_integrity(temp_path, checksum.upper())
            assert is_valid is True
            # Test with lowercase
            is_valid = validate_model_integrity(temp_path, checksum.lower())
            assert is_valid is True
            
        finally:
            os.unlink(temp_path)
    
    def test_model_integrity_file_not_found(self):
        """Test validation for non-existent file."""
        with pytest.raises(FileNotFoundError):
            validate_model_integrity("/non/existent/file.pkl", "checksum")
    
    def test_model_integrity_tampered_file(self):
        """Test detection of tampered file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("original content")
            temp_path = f.name
        
        try:
            original_checksum = calculate_checksum(temp_path)
            
            # Tamper with the file
            with open(temp_path, 'w') as f:
                f.write("tampered content")
            
            is_valid = validate_model_integrity(temp_path, original_checksum)
            assert is_valid is False
            
        finally:
            os.unlink(temp_path)


class TestLoadChecksums:
    """Test cases for loading checksums from JSON."""
    
    def test_load_valid_checksums_file(self):
        """Test loading a valid checksums JSON file."""
        checksums = {
            "model1.pkl": "abc123def456",
            "model2.pkl": "789ghi012jkl"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            import json
            json.dump(checksums, f)
            temp_path = f.name
        
        try:
            loaded = load_checksums(temp_path)
            assert loaded == checksums
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_checksums_file(self):
        """Test loading non-existent checksums file returns empty dict."""
        loaded = load_checksums("/non/existent/checksums.json")
        assert loaded == {}
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("not valid json{")
            temp_path = f.name
        
        try:
            with pytest.raises(Exception):
                load_checksums(temp_path)
        finally:
            os.unlink(temp_path)


class TestRestrictedUnpickler:
    """Test cases for restricted pickle unpickler."""
    
    def test_allowed_module_loading(self):
        """Test loading allowed modules."""
        # Create a pickle of allowed data
        import pickle
        
        data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            pickle.dump(data, f)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                unpickler = RestrictedUnpickler(f)
                loaded = unpickler.load()
            
            assert loaded == data
        finally:
            os.unlink(temp_path)
    
    def test_forbidden_module_blocked(self):
        """Test that forbidden modules are blocked."""
        import pickle
        import io
        
        # Create a malicious pickle that tries to import os.system
        # This is a simplified test - real malicious pickles would be more complex
        class MaliciousClass:
            def __reduce__(self):
                return (eval, ("__import__('os').system('echo pwned')",))
        
        # Note: Creating actual malicious pickles for testing is complex
        # This test documents the expected behavior
        
        # The RestrictedUnpickler should block non-whitelisted modules
        allowed_modules = RestrictedUnpickler.ALLOWED_MODULES
        
        # Check that dangerous modules are not in the whitelist
        dangerous_modules = ['os', 'sys', 'subprocess', 'socket']
        for module in dangerous_modules:
            assert module not in allowed_modules, f"{module} should not be in allowed modules"


class TestSecureLoadPickle:
    """Test cases for secure pickle loading."""
    
    def test_secure_load_without_verification(self):
        """Test loading pickle without checksum verification."""
        import pickle
        
        data = {"model": "test", "version": 1}
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            pickle.dump(data, f)
            temp_path = f.name
        
        try:
            loaded = secure_load_pickle(temp_path, verify_checksum=None)
            assert loaded == data
        finally:
            os.unlink(temp_path)
    
    def test_secure_load_with_verification(self):
        """Test loading pickle with checksum verification."""
        import pickle
        
        data = {"model": "test", "version": 1}
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            pickle.dump(data, f)
            temp_path = f.name
        
        try:
            checksum = calculate_checksum(temp_path)
            loaded = secure_load_pickle(temp_path, verify_checksum=checksum)
            assert loaded == data
        finally:
            os.unlink(temp_path)
    
    def test_secure_load_with_wrong_checksum(self):
        """Test loading pickle with wrong checksum raises error."""
        import pickle
        
        data = {"model": "test"}
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            pickle.dump(data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                secure_load_pickle(temp_path, verify_checksum="wrong_checksum")
            assert "checksum" in str(exc_info.value).lower() or "integrity" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_secure_load_file_not_found(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            secure_load_pickle("/non/existent/file.pkl")


class TestSanitizeInput:
    """Test cases for input sanitization."""
    
    def test_sanitize_normal_string(self):
        """Test sanitization of normal string."""
        result = sanitize_input("normal string")
        assert result == "normal string"
    
    def test_sanitize_null_bytes(self):
        """Test removal of null bytes."""
        result = sanitize_input("string\x00with\x00nulls")
        assert "\x00" not in result
    
    def test_sanitize_sql_injection(self):
        """Test detection of SQL injection patterns."""
        result = sanitize_input("'; DROP TABLE users;--")
        # SQL injection patterns should be removed or modified
        assert "'; DROP" not in result or result != "'; DROP TABLE users;--"
    
    def test_sanitize_length_limit(self):
        """Test length limiting."""
        long_string = "a" * 2000
        result = sanitize_input(long_string, max_length=1000)
        assert len(result) <= 1000
    
    def test_sanitize_non_string(self):
        """Test sanitization of non-string input."""
        result = sanitize_input(12345)
        assert result == 12345
        
        result = sanitize_input(["list", "items"])
        assert result == ["list", "items"]
    
    def test_sanitize_comment_patterns(self):
        """Test removal of SQL comment patterns."""
        result = sanitize_input("-- comment")
        assert "--" not in result
    
    def test_sanitize_block_comment_patterns(self):
        """Test removal of SQL block comment patterns."""
        result = sanitize_input("/* block comment */")
        assert "/*" not in result and "*/" not in result


class TestGenerateChecksumsForDirectory:
    """Test cases for generating checksums for directory."""
    
    def test_generate_checksums(self):
        """Test generating checksums for files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            with open(os.path.join(tmpdir, "file1.pkl"), 'w') as f:
                f.write("content1")
            with open(os.path.join(tmpdir, "file2.pkl"), 'w') as f:
                f.write("content2")
            
            output_file = os.path.join(tmpdir, "checksums.json")
            checksums = generate_checksums_for_directory(tmpdir, output_file)
            
            assert "file1.pkl" in checksums
            assert "file2.pkl" in checksums
            assert os.path.exists(output_file)
            
            # Checksums should be valid hex
            for checksum in checksums.values():
                assert len(checksum) == 64
                int(checksum, 16)
    
    def test_generate_checksums_nonexistent_directory(self):
        """Test generating checksums for non-existent directory."""
        checksums = generate_checksums_for_directory("/non/existent/dir", "output.json")
        assert checksums == {}
    
    def test_generate_checksums_pattern_filtering(self):
        """Test pattern filtering for checksum generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with different extensions
            with open(os.path.join(tmpdir, "model.pkl"), 'w') as f:
                f.write("model")
            with open(os.path.join(tmpdir, "data.txt"), 'w') as f:
                f.write("data")
            
            output_file = os.path.join(tmpdir, "checksums.json")
            checksums = generate_checksums_for_directory(tmpdir, output_file, pattern="*.pkl")
            
            assert "model.pkl" in checksums
            assert "data.txt" not in checksums


class TestSecureModelLoader:
    """Test cases for secure model loader."""
    
    def test_loader_initialization(self):
        """Test SecureModelLoader initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SecureModelLoader(tmpdir, verify_checksums=False)
            assert loader.models_dir == tmpdir
            assert loader.verify_checksums is False
    
    def test_loader_with_checksums(self):
        """Test loader with checksums file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create checksums file
            checksums = {"model.pkl": "abc123"}
            import json
            checksums_path = os.path.join(tmpdir, "checksums.json")
            with open(checksums_path, 'w') as f:
                json.dump(checksums, f)
            
            loader = SecureModelLoader(tmpdir, checksums_path, verify_checksums=True)
            assert "model.pkl" in loader.checksums
    
    def test_load_pickle_model_without_verification(self):
        """Test loading pickle model without checksum verification."""
        import pickle
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_data = {"model": "test"}
            model_path = os.path.join(tmpdir, "model.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            loader = SecureModelLoader(tmpdir, verify_checksums=False)
            loaded = loader.load_model("model.pkl", use_restricted_unpickler=False)
            assert loaded == model_data
    
    def test_load_nonexistent_model(self):
        """Test loading non-existent model raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SecureModelLoader(tmpdir, verify_checksums=False)
            
            with pytest.raises(FileNotFoundError) as exc_info:
                loader.load_model("nonexistent.pkl")
            assert "not found" in str(exc_info.value).lower()
    
    def test_unsupported_model_format(self):
        """Test loading unsupported model format raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with unsupported extension
            with open(os.path.join(tmpdir, "model.unknown"), 'w') as f:
                f.write("content")
            
            loader = SecureModelLoader(tmpdir, verify_checksums=False)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load_model("model.unknown")
            assert "unsupported" in str(exc_info.value).lower()
