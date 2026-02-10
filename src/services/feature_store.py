# Feature Store
# This module contains feature storage and retrieval functionality

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


class FeatureStore:
    """In-memory feature store for transaction features"""
    
    def __init__(self):
        self.features: Dict[str, Dict[str, Any]] = {}
    
    async def get_features(self, entity_id: str) -> Dict[str, Any]:
        """
        Get features for an entity
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Feature dictionary
        """
        if entity_id in self.features:
            return self.features[entity_id]
        
        # Return default features
        return {
            "transaction_count_24h": 0,
            "total_amount_24h": 0.0,
            "avg_transaction_amount": 0.0,
            "risk_score": 0,
            "first_transaction": None,
            "last_transaction": None
        }
    
    async def update_features(self, entity_id: str, features: Dict[str, Any]) -> None:
        """
        Update features for an entity
        
        Args:
            entity_id: Entity identifier
            features: New feature values
        """
        self.features[entity_id] = features
    
    async def get_transaction_history(self, entity_id: str, hours: int = 24) -> list:
        """
        Get transaction history for an entity
        
        Args:
            entity_id: Entity identifier
            hours: Time window in hours
            
        Returns:
            List of historical transactions
        """
        # TODO: Implement actual history retrieval
        return []
    
    async def increment_feature(self, entity_id: str, feature_name: str, amount: float = 1.0) -> None:
        """
        Increment a feature counter
        
        Args:
            entity_id: Entity identifier
            feature_name: Feature to increment
            amount: Increment amount
        """
        if entity_id not in self.features:
            self.features[entity_id] = {}
        
        current = self.features[entity_id].get(feature_name, 0)
        self.features[entity_id][feature_name] = current + amount


# Singleton instance
feature_store = FeatureStore()
