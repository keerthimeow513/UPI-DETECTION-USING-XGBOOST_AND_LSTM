"""Inference module for UPI Fraud Detection API."""

from .service import FraudDetectionService
from .schemas import TransactionRequest, PredictionResponse

__all__ = ['FraudDetectionService', 'TransactionRequest', 'PredictionResponse']
__version__ = "1.0.0"
