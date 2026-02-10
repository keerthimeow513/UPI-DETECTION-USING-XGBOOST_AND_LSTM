"""
Redis-based Feature Store for User Transaction History

This module provides a Redis-backed feature store for managing user transaction
histories used by the LSTM model. It supports storing transaction features,
retrieving historical sequences, and computing velocity features.

Features:
    - Persistent transaction history per user
    - Automatic expiration (TTL) to prevent unbounded growth
    - Velocity features (transactions per hour)
    - Graceful fallback when Redis is unavailable

Usage:
    from utils.feature_store import UserFeatureStore
    
    store = UserFeatureStore()
    store.add_transaction("user@upi", features)
    history = store.get_history("user@upi")
    count = store.get_transaction_count("user@upi", hours=1)

Dependencies:
    - redis-py: Redis client library
    - numpy: For array operations
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np

from utils.config import settings

logger = logging.getLogger(__name__)


class FeatureStoreError(Exception):
    """Custom exception for feature store operations."""
    pass


class UserFeatureStore:
    """
    Redis-based feature store for user transaction history.
    
    This class manages user transaction histories stored in Redis, enabling
    the LSTM model to access real behavioral patterns instead of mocked data.
    
    Attributes:
        redis: Redis client instance
        lookback: Number of historical transactions to retrieve (default: 10)
        enabled: Whether the feature store is enabled
    
    Example:
        store = UserFeatureStore()
        
        # Add a transaction
        store.add_transaction("user@upi", features_array)
        
        # Get history for LSTM input
        history = store.get_history("user@upi")
        if history is not None:
            # history shape: (10, n_features)
            pass
    """
    
    def __init__(self, redis_url: str = None, lookback: int = 10):
        """
        Initialize the UserFeatureStore.
        
        Args:
            redis_url: Redis connection URL. If None, uses settings.REDIS_URL.
            lookback: Number of historical transactions to maintain.
        
        Raises:
            FeatureStoreError: If Redis connection fails and strict mode is enabled.
        """
        self.lookback = lookback
        self.enabled = self._check_enabled()
        self.redis = None
        
        if self.enabled:
            try:
                import redis
                url = redis_url or settings.REDIS_URL
                self.redis = redis.from_url(url, decode_responses=True)
                # Test connection
                self.redis.ping()
                logger.info(f"Feature store connected to Redis at {url}")
            except ImportError:
                logger.warning("redis-py not installed. Feature store disabled.")
                self.enabled = False
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {str(e)}. Feature store disabled.")
                self.enabled = False
    
    def _check_enabled(self) -> bool:
        """Check if feature store is enabled via settings."""
        # Check for explicit FEATURE_STORE_ENABLED setting
        try:
            return getattr(settings, 'FEATURE_STORE_ENABLED', True)
        except:
            return True
    
    def add_transaction(self, user_id: str, features: np.ndarray) -> bool:
        """
        Add a transaction to user's history.
        
        Stores transaction features with timestamp in Redis. Maintains only
        the most recent 'lookback * 2' transactions to limit memory usage.
        Sets a 7-day TTL to prevent unbounded growth.
        
        Args:
            user_id: Unique identifier for the user (e.g., UPI ID).
            features: Numpy array of transaction features.
        
        Returns:
            True if successful, False otherwise.
        
        Example:
            features = np.array([100.0, 0.5, 0.3, ...])
            store.add_transaction("user@upi", features)
        """
        if not self.enabled or self.redis is None:
            logger.debug("Feature store disabled, skipping transaction storage")
            return False
        
        try:
            key = f"user:{user_id}:transactions"
            timestamp = datetime.now().isoformat()
            data = {
                'timestamp': timestamp,
                'features': features.tolist() if isinstance(features, np.ndarray) else features
            }
            
            # Add to list (LPUSH for most recent first)
            self.redis.lpush(key, json.dumps(data))
            
            # Trim to keep only needed transactions (keep extra for safety)
            self.redis.ltrim(key, 0, self.lookback * 2 - 1)
            
            # Set TTL to 7 days
            self.redis.expire(key, 86400 * 7)
            
            logger.debug(f"Stored transaction for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store transaction for user {user_id}: {str(e)}")
            return False
    
    def get_history(self, user_id: str) -> Optional[np.ndarray]:
        """
        Get user's transaction history for LSTM.
        
        Retrieves the most recent 'lookback' transactions for the specified user.
        Returns None if insufficient history is available.
        
        Args:
            user_id: Unique identifier for the user.
        
        Returns:
            Numpy array of shape (lookback, n_features) if sufficient history exists,
            None otherwise.
        
        Example:
            history = store.get_history("user@upi")
            if history is not None:
                assert history.shape == (10, n_features)
        """
        if not self.enabled or self.redis is None:
            logger.debug("Feature store disabled, returning None")
            return None
        
        try:
            key = f"user:{user_id}:transactions"
            transactions = self.redis.lrange(key, 0, self.lookback - 1)
            
            if len(transactions) < self.lookback:
                logger.debug(f"Insufficient history for user {user_id}: {len(transactions)}/{self.lookback}")
                return None
            
            # Parse and extract features (most recent first from Redis)
            # Reverse to get chronological order (oldest first) for LSTM
            features = [json.loads(t)['features'] for t in reversed(transactions)]
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Failed to retrieve history for user {user_id}: {str(e)}")
            return None
    
    def get_transaction_count(self, user_id: str, hours: int = 1) -> int:
        """
        Count transactions in last N hours (for velocity features).
        
        Counts how many transactions the user has made within the specified
        time window. Used for computing velocity-based fraud detection features.
        
        Args:
            user_id: Unique identifier for the user.
            hours: Time window in hours (default: 1).
        
        Returns:
            Number of transactions in the specified time window.
        
        Example:
            # Count transactions in last hour
            count = store.get_transaction_count("user@upi", hours=1)
            if count > 5:
                # Flag high velocity
                pass
        """
        if not self.enabled or self.redis is None:
            return 0
        
        try:
            key = f"user:{user_id}:transactions"
            transactions = self.redis.lrange(key, 0, -1)
            
            if not transactions:
                return 0
            
            cutoff = datetime.now() - timedelta(hours=hours)
            
            count = 0
            for t in transactions:
                try:
                    data = json.loads(t)
                    tx_time = datetime.fromisoformat(data['timestamp'])
                    if tx_time > cutoff:
                        count += 1
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Skip malformed entries
                    continue
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to count transactions for user {user_id}: {str(e)}")
            return 0
    
    def get_amount_in_window(self, user_id: str, hours: int = 1, 
                             amount_index: int = 0) -> float:
        """
        Calculate total transaction amount in the last N hours.
        
        Sums up transaction amounts within the specified time window.
        Assumes the amount is stored at the specified feature index.
        
        Args:
            user_id: Unique identifier for the user.
            hours: Time window in hours (default: 1).
            amount_index: Index of the amount feature in the feature vector.
        
        Returns:
            Total amount transacted in the specified window.
        """
        if not self.enabled or self.redis is None:
            return 0.0
        
        try:
            key = f"user:{user_id}:transactions"
            transactions = self.redis.lrange(key, 0, -1)
            
            if not transactions:
                return 0.0
            
            cutoff = datetime.now() - timedelta(hours=hours)
            
            total_amount = 0.0
            for t in transactions:
                try:
                    data = json.loads(t)
                    tx_time = datetime.fromisoformat(data['timestamp'])
                    if tx_time > cutoff:
                        features = data['features']
                        if isinstance(features, list) and len(features) > amount_index:
                            total_amount += float(features[amount_index])
                except (json.JSONDecodeError, KeyError, ValueError, TypeError, IndexError):
                    # Skip malformed entries
                    continue
            
            return total_amount
            
        except Exception as e:
            logger.error(f"Failed to calculate amount for user {user_id}: {str(e)}")
            return 0.0
    
    def clear_user_history(self, user_id: str) -> bool:
        """
        Clear all transaction history for a user.
        
        Useful for testing or when a user requests data deletion.
        
        Args:
            user_id: Unique identifier for the user.
        
        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled or self.redis is None:
            return False
        
        try:
            key = f"user:{user_id}:transactions"
            self.redis.delete(key)
            logger.info(f"Cleared history for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear history for user {user_id}: {str(e)}")
            return False
    
    def get_user_stats(self, user_id: str) -> dict:
        """
        Get statistics for a user's transaction history.
        
        Returns:
            Dictionary containing:
                - total_transactions: Total stored transactions
                - transactions_last_hour: Count in last hour
                - transactions_last_24h: Count in last 24 hours
                - amount_last_hour: Total amount in last hour
                - has_sufficient_history: Whether enough history for LSTM
        """
        stats = {
            'total_transactions': 0,
            'transactions_last_hour': 0,
            'transactions_last_24h': 0,
            'amount_last_hour': 0.0,
            'has_sufficient_history': False
        }
        
        if not self.enabled or self.redis is None:
            return stats
        
        try:
            key = f"user:{user_id}:transactions"
            total = self.redis.llen(key)
            stats['total_transactions'] = total
            stats['has_sufficient_history'] = total >= self.lookback
            
            stats['transactions_last_hour'] = self.get_transaction_count(user_id, hours=1)
            stats['transactions_last_24h'] = self.get_transaction_count(user_id, hours=24)
            stats['amount_last_hour'] = self.get_amount_in_window(user_id, hours=1)
            
        except Exception as e:
            logger.error(f"Failed to get stats for user {user_id}: {str(e)}")
        
        return stats


# Global instance for easy import
_feature_store_instance: Optional[UserFeatureStore] = None


def get_feature_store() -> UserFeatureStore:
    """
    Get the global feature store instance.
    
    Returns:
        UserFeatureStore: Singleton instance of the feature store.
    """
    global _feature_store_instance
    if _feature_store_instance is None:
        _feature_store_instance = UserFeatureStore()
    return _feature_store_instance
