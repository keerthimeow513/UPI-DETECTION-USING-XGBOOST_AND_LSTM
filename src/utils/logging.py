# Logging Utilities
# This module contains logging configuration and utilities

import logging
from datetime import datetime
from pathlib import Path


def setup_logger(
    name: str = "upi_fraud_detection",
    log_file: str = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_transaction(
    logger: logging.Logger,
    transaction_id: str,
    prediction: bool,
    probability: float,
    metadata: dict = None
) -> None:
    """
    Log transaction prediction
    
    Args:
        logger: Logger instance
        transaction_id: Transaction identifier
        prediction: Fraud prediction result
        probability: Fraud probability
        metadata: Additional metadata
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "transaction_id": transaction_id,
        "is_fraud": prediction,
        "fraud_probability": probability,
        **(metadata or {})
    }
    
    logger.info(f"Transaction prediction: {log_data}")


# Create default logger
logger = setup_logger()


class LoggerMixin:
    """Mixin class to add logging capability"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(self.__class__.__name__)
