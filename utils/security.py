"""
UPI Fraud Detection - Security Utilities Module

This module provides security utilities for the UPI Fraud Detection system.
It handles:
- File integrity verification with SHA256 checksums
- Secure model loading with restricted unpickler
- Input sanitization utilities
- Model integrity validation

Example:
    from utils.security import calculate_checksum, validate_model_integrity
    
    # Calculate checksum
    checksum = calculate_checksum('model.pkl')
    
    # Validate model integrity
    is_valid = validate_model_integrity('model.pkl', expected_checksum)
"""

import hashlib
import os
import json
import pickle
import sys
from typing import Dict, Optional, Set, Any
from utils.logger import setup_logger

logger = setup_logger()


class ModelSecurityError(Exception):
    """Custom exception for model security violations."""
    pass


class RestrictedUnpickler(pickle.Unpickler):
    """
    Restricted pickle unpickler that only allows safe modules.
    
    This prevents arbitrary code execution vulnerabilities that can occur
    when loading untrusted pickle files. Only whitelisted modules are allowed.
    
    Attributes:
        ALLOWED_MODULES (Set[str]): Set of allowed module prefixes
    """
    
    ALLOWED_MODULES: Set[str] = {
        'sklearn',
        'xgboost',
        'lightgbm',
        'numpy',
        'scipy',
        'pandas',
        'collections',
        'builtins',
        'copyreg',
        '__builtin__',
        'numpy.core.multiarray',
        'numpy.random._pickle',
        'xgboost.sklearn',
        'xgboost.core',
        'sklearn.ensemble',
        'sklearn.tree',
        'sklearn.preprocessing',
        '_codecs',
    }
    
    def find_class(self, module: str, name: str) -> Any:
        """
        Override find_class to restrict module loading.
        
        Only allows classes from whitelisted modules to prevent
        arbitrary code execution attacks.
        
        Args:
            module (str): Module name attempting to load
            name (str): Class name attempting to load
            
        Returns:
            Any: The class object if allowed
            
        Raises:
            ModelSecurityError: If module is not in whitelist
        """
        # Check if module is in allowed list (also check parent modules)
        module_parts = module.split('.')
        is_allowed = any(
            '.'.join(module_parts[:i+1]) in self.ALLOWED_MODULES
            for i in range(len(module_parts))
        )
        
        if not is_allowed:
            raise ModelSecurityError(
                f"Security violation: Attempted to load forbidden module '{module}.{name}'. "
                f"This may indicate a malicious pickle file."
            )
        
        # Use standard import mechanism
        try:
            return super().find_class(module, name)
        except (ImportError, AttributeError) as e:
            raise ModelSecurityError(
                f"Failed to import {module}.{name}: {str(e)}"
            )


def calculate_checksum(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate the checksum of a file.
    
    Computes a cryptographic hash of the file contents for integrity
    verification. Uses SHA256 by default for security.
    
    Args:
        file_path (str): Path to the file to hash
        algorithm (str): Hash algorithm to use ('sha256', 'sha512', 'md5')
                        Defaults to 'sha256'
    
    Returns:
        str: Hexadecimal string of the file hash
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If unsupported algorithm specified
        
    Example:
        >>> checksum = calculate_checksum('model.pkl')
        >>> print(checksum)
        'a1b2c3d4e5f6...'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Select hash algorithm
    if algorithm == 'sha256':
        hasher = hashlib.sha256()
    elif algorithm == 'sha512':
        hasher = hashlib.sha512()
    elif algorithm == 'md5':
        hasher = hashlib.md5()
        logger.warning("MD5 is not recommended for security purposes. Use SHA256.")
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Read file in chunks to handle large files efficiently
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
    except IOError as e:
        raise IOError(f"Failed to read file {file_path}: {str(e)}")
    
    return hasher.hexdigest()


def validate_model_integrity(
    file_path: str, 
    expected_checksum: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Validate the integrity of a model file.
    
    Compares the actual file checksum against an expected value to
    detect tampering or corruption.
    
    Args:
        file_path (str): Path to the model file
        expected_checksum (str): Expected checksum value
        algorithm (str): Hash algorithm used for checksum
        
    Returns:
        bool: True if checksums match, False otherwise
        
    Raises:
        FileNotFoundError: If model file does not exist
        
    Example:
        >>> is_valid = validate_model_integrity(
        ...     'model.pkl',
        ...     'a1b2c3d4e5f6...'
        ... )
        >>> if is_valid:
        ...     print("Model integrity verified")
    """
    try:
        actual_checksum = calculate_checksum(file_path, algorithm)
        is_valid = actual_checksum.lower() == expected_checksum.lower()
        
        if not is_valid:
            logger.error(
                f"Model integrity check failed for {file_path}\n"
                f"Expected: {expected_checksum}\n"
                f"Actual:   {actual_checksum}"
            )
        else:
            logger.info(f"Model integrity verified for {os.path.basename(file_path)}")
        
        return is_valid
        
    except FileNotFoundError:
        logger.error(f"Model file not found: {file_path}")
        raise


def load_checksums(checksums_file: str) -> Dict[str, str]:
    """
    Load checksums from a JSON file.
    
    Args:
        checksums_file (str): Path to the checksums JSON file
        
    Returns:
        Dict[str, str]: Dictionary mapping filenames to checksums
        
    Raises:
        FileNotFoundError: If checksums file does not exist
        json.JSONDecodeError: If file contains invalid JSON
        
    Example:
        >>> checksums = load_checksums('checksums.json')
        >>> print(checksums['model.pkl'])
        'a1b2c3d4e5f6...'
    """
    if not os.path.exists(checksums_file):
        logger.warning(f"Checksums file not found: {checksums_file}")
        return {}
    
    try:
        with open(checksums_file, 'r') as f:
            checksums = json.load(f)
        logger.info(f"Loaded checksums from {checksums_file}")
        return checksums
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in checksums file: {str(e)}")
        raise


def secure_load_pickle(file_path: str, verify_checksum: Optional[str] = None) -> Any:
    """
    Securely load a pickle file with optional integrity verification.
    
    Uses RestrictedUnpickler to prevent arbitrary code execution
    and optionally validates file integrity.
    
    Args:
        file_path (str): Path to the pickle file
        verify_checksum (Optional[str]): Expected checksum for verification
        
    Returns:
        Any: The unpickled object
        
    Raises:
        FileNotFoundError: If file does not exist
        ModelSecurityError: If security violation detected
        ValueError: If checksum verification fails
        
    Example:
        >>> try:
        ...     model = secure_load_pickle('model.pkl', expected_checksum='abc123')
        ... except ModelSecurityError as e:
        ...     print(f"Security violation: {e}")
    """
    # Verify file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Model file not found: {file_path}\n"
            f"Please ensure models are trained and saved to the correct location."
        )
    
    # Verify checksum if provided
    if verify_checksum:
        if not validate_model_integrity(file_path, verify_checksum):
            raise ValueError(
                f"Checksum verification failed for {file_path}. "
                f"The file may be corrupted or tampered with."
            )
    
    # Load with restricted unpickler
    try:
        with open(file_path, 'rb') as f:
            unpickler = RestrictedUnpickler(f)
            obj = unpickler.load()
        logger.info(f"Securely loaded pickle file: {os.path.basename(file_path)}")
        return obj
    except ModelSecurityError:
        raise
    except Exception as e:
        raise RuntimeError(
            f"Failed to load pickle file {file_path}: {str(e)}"
        )


def sanitize_input(value: Any, max_length: int = 1000) -> Any:
    """
    Sanitize input values to prevent injection attacks.
    
    Args:
        value (Any): Input value to sanitize
        max_length (int): Maximum allowed length for string values
        
    Returns:
        Any: Sanitized value
        
    Example:
        >>> safe_value = sanitize_input(user_input)
    """
    if isinstance(value, str):
        # Limit length
        if len(value) > max_length:
            logger.warning(f"Input truncated from {len(value)} to {max_length} characters")
            value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Basic SQL injection prevention (remove common patterns)
        dangerous_patterns = ['--', '/*', '*/', ';--', "'; DROP", "'; SELECT"]
        for pattern in dangerous_patterns:
            if pattern in value.lower():
                logger.warning(f"Potentially dangerous pattern detected in input: {pattern}")
                value = value.replace(pattern, '')
    
    return value


def generate_checksums_for_directory(
    directory: str, 
    output_file: str,
    pattern: str = '*.pkl'
) -> Dict[str, str]:
    """
    Generate checksums for all files matching a pattern in a directory.
    
    Args:
        directory (str): Directory to scan
        output_file (str): Path to save checksums JSON file
        pattern (str): File pattern to match (default: '*.pkl')
        
    Returns:
        Dict[str, str]: Dictionary of filenames to checksums
        
    Example:
        >>> checksums = generate_checksums_for_directory(
        ...     '02_models/artifacts',
        ...     'checksums.json'
        ... )
    """
    import fnmatch
    
    checksums = {}
    
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return checksums
    
    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename, pattern):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    checksum = calculate_checksum(file_path)
                    checksums[filename] = checksum
                    logger.info(f"Generated checksum for {filename}: {checksum[:16]}...")
                except Exception as e:
                    logger.error(f"Failed to generate checksum for {filename}: {str(e)}")
    
    # Save to JSON file
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(checksums, f, indent=2)
    
    logger.info(f"Saved {len(checksums)} checksums to {output_file}")
    return checksums


class SecureModelLoader:
    """
    Secure model loader with integrity verification and restricted unpickling.
    
    This class provides a centralized way to load ML models with security
    checks including file existence, checksum validation, and safe deserialization.
    
    Attributes:
        models_dir (str): Directory containing model files
        checksums (Dict[str, str]): Loaded checksums dictionary
        verify_checksums (bool): Whether to enforce checksum verification
        
    Example:
        >>> loader = SecureModelLoader('02_models/artifacts', 'checksums.json')
        >>> model = loader.load_model('xgb_model.pkl')
    """
    
    def __init__(
        self, 
        models_dir: str,
        checksums_file: Optional[str] = None,
        verify_checksums: bool = True
    ):
        """
        Initialize the secure model loader.
        
        Args:
            models_dir (str): Directory containing model files
            checksums_file (Optional[str]): Path to checksums JSON file
            verify_checksums (bool): Whether to enforce checksum verification
        """
        self.models_dir = models_dir
        self.verify_checksums = verify_checksums
        self.checksums = {}
        
        if checksums_file and os.path.exists(checksums_file):
            self.checksums = load_checksums(checksums_file)
        elif verify_checksums:
            logger.warning(
                f"Checksums file not provided or not found: {checksums_file}. "
                f"Model integrity verification will be skipped."
            )
    
    def load_model(self, model_name: str, use_restricted_unpickler: bool = True) -> Any:
        """
        Load a model file with security checks.
        
        Args:
            model_name (str): Name of the model file
            use_restricted_unpickler (bool): Whether to use restricted unpickler
            
        Returns:
            Any: The loaded model
            
        Raises:
            FileNotFoundError: If model file does not exist
            ModelSecurityError: If security check fails
            ValueError: If checksum verification fails
        """
        model_path = os.path.join(self.models_dir, model_name)
        
        # Check file existence
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please ensure the model has been trained and saved.\n"
                f"Run: python 03_training/train.py"
            )
        
        # Verify checksum if available and verification enabled
        expected_checksum = self.checksums.get(model_name)
        if self.verify_checksums and expected_checksum:
            if not validate_model_integrity(model_path, expected_checksum):
                raise ValueError(
                    f"Model integrity check failed for {model_name}. "
                    f"The file may be corrupted or tampered with."
                )
        
        # Load based on file type
        if model_name.endswith('.pkl'):
            if use_restricted_unpickler:
                return secure_load_pickle(model_path, expected_checksum)
            else:
                import joblib
                return joblib.load(model_path)
        elif model_name.endswith('.h5'):
            # Keras/TensorFlow models - no custom unpickler needed
            import tensorflow as tf
            return tf.keras.models.load_model(model_path)
        else:
            raise ValueError(f"Unsupported model format: {model_name}")
