"""
Configuration Management Module

This module provides centralized, type-safe configuration management using
Pydantic Settings. It supports environment variable loading from .env files
and provides validation for all configuration values.

Features:
    - Type-safe configuration with Pydantic v2
    - Automatic .env file loading
    - Environment-specific configurations
    - Validation for required fields
    - Default values for development

Usage:
    from utils.config import settings
    
    # Access configuration values
    host = settings.API_HOST
    port = settings.API_PORT
    
    # Check environment
    if settings.is_development:
        print("Running in development mode")

Environment Variables:
    All configuration can be overridden via environment variables.
    See .env.example for available options.

Example:
    # Set environment variable
    export API_PORT=9000
    
    # Or create a .env file
    echo "API_PORT=9000" > .env
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    This class defines all configuration options for the UPI Fraud Detection
    system. Values can be set via:
    1. Environment variables (highest priority)
    2. .env file in project root
    3. Default values defined here (lowest priority)
    
    Attributes:
        API_HOST: Host address for the API server
        API_PORT: Port number for the API server
        API_URL: Full URL for the API endpoint
        ENVIRONMENT: Current environment (development, staging, production)
        CORS_ORIGINS: List of allowed CORS origins
        RATE_LIMIT_REQUESTS: Max requests per rate limit period
        RATE_LIMIT_PERIOD: Rate limit period in seconds
        MODEL_PATH: Path to model artifacts
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
        REDIS_URL: Redis connection URL
        API_KEY_SECRET: Secret key for API authentication
        MAX_TRANSACTION_AMOUNT: Maximum allowed transaction amount
    """
    
    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        # Load from .env file in project root
        env_file='.env',
        env_file_encoding='utf-8',
        # Allow environment variables to override
        env_nested_delimiter='__',
        # Extra fields are forbidden for security
        extra='forbid',
        # Case sensitivity
        case_sensitive=False,
    )
    
    # =============================================================================
    # API Configuration
    # =============================================================================
    API_HOST: str = Field(
        default="0.0.0.0",
        description="Host address for the API server"
    )
    
    API_PORT: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Port number for the API server"
    )
    
    API_URL: str = Field(
        default="http://localhost:8000",
        description="Full URL for the API endpoint"
    )
    
    # =============================================================================
    # Environment Settings
    # =============================================================================
    ENVIRONMENT: str = Field(
        default="development",
        pattern="^(development|staging|production|test)$",
        description="Current environment (development, staging, production, test)"
    )
    
    # =============================================================================
    # CORS Configuration
    # =============================================================================
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # =============================================================================
    # Rate Limiting Configuration
    # =============================================================================
    RATE_LIMIT_REQUESTS: int = Field(
        default=10,
        ge=1,
        description="Maximum number of requests allowed per period"
    )
    
    RATE_LIMIT_PERIOD: int = Field(
        default=60,
        ge=1,
        description="Rate limit period in seconds"
    )
    
    # =============================================================================
    # Model Configuration
    # =============================================================================
    MODEL_PATH: str = Field(
        default="02_models/artifacts/",
        description="Path to model artifacts directory"
    )
    
    # =============================================================================
    # Logging Configuration
    # =============================================================================
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # =============================================================================
    # Redis Configuration
    # =============================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    FEATURE_STORE_ENABLED: bool = Field(
        default=True,
        description="Enable Redis-based feature store for user transaction history"
    )
    
    # =============================================================================
    # Security Configuration
    # =============================================================================
    API_KEY_SECRET: str = Field(
        default="your-secret-key-here",
        min_length=16,
        description="Secret key for API authentication"
    )
    
    # =============================================================================
    # Transaction Limits
    # =============================================================================
    MAX_TRANSACTION_AMOUNT: float = Field(
        default=10000000.0,
        ge=0,
        description="Maximum allowed transaction amount in INR"
    )
    
    # =============================================================================
    # Validators
    # =============================================================================
    
    @field_validator('CORS_ORIGINS')
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """
        Validate CORS origins format.
        
        Args:
            v: Comma-separated string of origins
            
        Returns:
            The validated string
            
        Raises:
            ValueError: If any origin is invalid
        """
        origins = [origin.strip() for origin in v.split(',')]
        for origin in origins:
            if origin and not (origin.startswith('http://') or origin.startswith('https://') or origin == '*'):
                raise ValueError(f"Invalid CORS origin: {origin}. Must start with http:// or https://")
        return v
    
    # =============================================================================
    # Properties
    # =============================================================================
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Get CORS origins as a list.
        
        Returns:
            List of allowed origin URLs
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == 'development'
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.ENVIRONMENT.lower() == 'staging'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == 'production'
    
    @property
    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.ENVIRONMENT.lower() == 'test'
    
    @property
    def predict_endpoint(self) -> str:
        """Get the full prediction endpoint URL."""
        return f"{self.API_URL.rstrip('/')}/predict"
    
    @property
    def model_path_absolute(self) -> str:
        """Get absolute path to model artifacts."""
        if os.path.isabs(self.MODEL_PATH):
            return self.MODEL_PATH
        # Assume relative to project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return os.path.join(project_root, self.MODEL_PATH)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    This function provides a singleton-like access to settings,
    ensuring the configuration is loaded only once and cached
    for subsequent accesses.
    
    Returns:
        Settings: The application settings instance
        
    Example:
        settings = get_settings()
        print(settings.API_HOST)
    """
    return Settings()


# Global settings instance for easy import
settings = get_settings()
