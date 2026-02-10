# Fraud Detection Service
# This module contains the core fraud detection service

from datetime import datetime
from typing import Optional
import numpy as np
from src.api.schemas import TransactionRequest, FraudPredictionResponse
from src.services.feature_store import feature_store
from src.utils.preprocessing import preprocess_transaction
from src.utils.logging import logger


class FraudDetectionService:
    """Service for detecting fraudulent transactions"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.threshold = 0.5
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model_loaded
    
    async def predict(self, request: TransactionRequest) -> FraudPredictionResponse:
        """
        Predict if a transaction is fraudulent
        
        Args:
            request: Transaction details
            
        Returns:
            Fraud prediction response
        """
        import time
        start_time = time.time()
        
        # Get features from feature store
        features = await feature_store.get_features(request.sender_id)
        
        # Preprocess transaction
        processed_features = preprocess_transaction(request, features)
        
        # Make prediction
        if self.model is None:
            # Placeholder prediction if model not loaded
            is_fraud = False
            probability = 0.1
        else:
            probability = self.model.predict_proba([processed_features])[0][1]
            is_fraud = probability > self.threshold
        
        # Calculate risk score (0-100)
        risk_score = int(min(probability * 100, 100))
        
        prediction_time = (time.time() - start_time) * 1000
        
        return FraudPredictionResponse(
            transaction_id=request.transaction_id,
            is_fraud=is_fraud,
            fraud_probability=round(probability, 4),
            risk_score=risk_score,
            confidence=round(1 - probability + 0.5, 4),  # Placeholder confidence
            features_analyzed=len(processed_features),
            prediction_time_ms=round(prediction_time, 2),
            timestamp=datetime.utcnow()
        )
    
    def load_model(self, model_path: str) -> None:
        """
        Load model from path
        
        Args:
            model_path: Path to model file
        """
        from src.models.train import load_model
        
        try:
            self.model = load_model(model_path)
            self.model_loaded = True
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise


# Singleton instance
fraud_detection_service = FraudDetectionService()
