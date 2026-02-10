#!/bin/bash
# Docker Entrypoint Script for UPI Fraud Detection API
# Performs pre-startup checks and waits for dependencies

set -e  # Exit immediately if a command exits with a non-zero status

echo "=========================================="
echo "FraudShield API - Starting Up"
echo "=========================================="

# ============================================================================
# CHECK 1: Wait for Redis to be ready
# ============================================================================
if [ -n "$REDIS_URL" ]; then
    echo ""
    echo "⏳ Waiting for Redis to be ready..."
    
    # Extract host from REDIS_URL (format: redis://host:port/db)
    REDIS_HOST=$(echo $REDIS_URL | sed -E 's|redis://([^:/]+).*|\1|')
    REDIS_PORT=$(echo $REDIS_URL | sed -E 's|redis://[^:]+:([0-9]+).*|\1|')
    
    # Default to standard Redis port if parsing failed
    REDIS_PORT=${REDIS_PORT:-6379}
    REDIS_HOST=${REDIS_HOST:-redis}
    
    # Wait for Redis with timeout (60 seconds)
    TIMEOUT=60
    ELAPSED=0
    
    until nc -z $REDIS_HOST $REDIS_PORT; do
        if [ $ELAPSED -ge $TIMEOUT ]; then
            echo "❌ ERROR: Redis connection timeout after ${TIMEOUT}s"
            echo "   Host: $REDIS_HOST"
            echo "   Port: $REDIS_PORT"
            exit 1
        fi
        
        echo "   Still waiting for Redis at $REDIS_HOST:$REDIS_PORT... (${ELAPSED}s)"
        sleep 1
        ELAPSED=$((ELAPSED + 1))
    done
    
    echo "✅ Redis is ready! ($REDIS_HOST:$REDIS_PORT)"
else
    echo "⚠️  WARNING: REDIS_URL not set, skipping Redis check"
fi

# ============================================================================
# CHECK 2: Verify model artifacts exist
# ============================================================================
echo ""
echo "🔍 Verifying model artifacts..."

MODEL_DIR="02_models/artifacts"
MISSING_MODELS=0

# Check LSTM model
if [ ! -f "$MODEL_DIR/lstm_model.h5" ]; then
    echo "❌ ERROR: LSTM model not found! ($MODEL_DIR/lstm_model.h5)"
    MISSING_MODELS=$((MISSING_MODELS + 1))
else
    echo "✅ LSTM model found"
fi

# Check XGBoost model
if [ ! -f "$MODEL_DIR/xgb_model.pkl" ]; then
    echo "❌ ERROR: XGBoost model not found! ($MODEL_DIR/xgb_model.pkl)"
    MISSING_MODELS=$((MISSING_MODELS + 1))
else
    echo "✅ XGBoost model found"
fi

# Check scaler
if [ ! -f "$MODEL_DIR/scaler.pkl" ]; then
    echo "❌ ERROR: Scaler not found! ($MODEL_DIR/scaler.pkl)"
    MISSING_MODELS=$((MISSING_MODELS + 1))
else
    echo "✅ Scaler found"
fi

# Check label encoders
if [ ! -f "$MODEL_DIR/label_encoders.pkl" ]; then
    echo "❌ ERROR: Label encoders not found! ($MODEL_DIR/label_encoders.pkl)"
    MISSING_MODELS=$((MISSING_MODELS + 1))
else
    echo "✅ Label encoders found"
fi

# Exit if any models are missing
if [ $MISSING_MODELS -gt 0 ]; then
    echo ""
    echo "❌ CRITICAL: $MISSING_MODELS model artifact(s) missing!"
    echo "   Please ensure model files are present in $MODEL_DIR/"
    exit 1
fi

# ============================================================================
# CHECK 3: Verify configuration files
# ============================================================================
echo ""
echo "🔍 Verifying configuration..."

if [ ! -f "07_configs/config.yaml" ]; then
    echo "⚠️  WARNING: Config file not found (07_configs/config.yaml)"
    echo "   Using default configuration"
else
    echo "✅ Configuration file found"
fi

# ============================================================================
# CHECK 4: Display environment info
# ============================================================================
echo ""
echo "📋 Environment Configuration:"
echo "   - ENVIRONMENT: ${ENVIRONMENT:-development}"
echo "   - API_HOST: ${API_HOST:-0.0.0.0}"
echo "   - API_PORT: ${API_PORT:-8000}"
echo "   - LOG_LEVEL: ${LOG_LEVEL:-INFO}"
echo "   - REDIS_URL: ${REDIS_URL:-not set}"
echo "   - FEATURE_STORE_ENABLED: ${FEATURE_STORE_ENABLED:-true}"

# ============================================================================
# CHECK 5: Health check of API module
# ============================================================================
echo ""
echo "🧪 Testing API import..."
if python -c "import sys; sys.path.insert(0, '.'); from 04_inference.api import app; print('✅ API module imported successfully')" 2>/dev/null; then
    echo "✅ API module ready"
else
    echo "⚠️  WARNING: Could not pre-import API module (will retry on startup)"
fi

# ============================================================================
# STARTUP
# ============================================================================
echo ""
echo "=========================================="
echo "🚀 Starting UPI Fraud Detection API..."
echo "=========================================="
echo ""

# Execute the main command passed to the entrypoint
exec "$@"
