# Architecture Documentation

Technical architecture overview of the UPI Fraud Detection System.

## System Overview

The UPI Fraud Detection System is a real-time hybrid AI platform designed to detect fraudulent transactions on the Unified Payments Interface (UPI). The system combines deep learning and gradient boosting models with domain-specific rules to provide accurate, explainable fraud detection.

### Core Design Principles

1. **Hybrid Intelligence**: Combines LSTM for sequential patterns and XGBoost for feature-based classification
2. **Explainability First**: Every decision includes human-readable explanations via SHAP values
3. **Defense in Depth**: Multiple security layers (ML + Domain Rules)
4. **Real-time Processing**: Sub-second latency for transaction analysis
5. **Scalability**: Modular architecture supports horizontal scaling

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Mobile App  │  │ Web App     │  │ Payment GW  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/WSS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Server                         │   │
│  │  • Rate Limiting     • CORS      • Request Validation   │   │
│  │  • Load Balancing    • Auth      • Request Logging      │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRAUD DETECTION ENGINE                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FraudDetectionService                      │   │
│  │  • Request Validation     • Response Aggregation       │   │
│  │  • Feature Engineering    • Domain Rule Application    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                    │
│              ┌──────────────┼──────────────┐                    │
│              ▼              ▼              ▼                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │   LSTM      │  │   XGBoost   │  │   Domain Rules      │     │
│  │   Model     │  │   Model     │  │   Engine            │     │
│  │  (50%)      │  │  (50%)      │  │   (Safety Layer)    │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
│                             │                                    │
│              ┌──────────────┴──────────────┐                    │
│              ▼                             ▼                    │
│  ┌─────────────────────┐      ┌─────────────────────────────┐  │
│  │     SHAP            │      │     Feature Store          │  │
│  │  Explainability     │      │  (Redis/In-Memory)         │  │
│  └─────────────────────┘      └─────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │   Model     │  │ Transaction │  │     Logs           │     │
│  │ Artifacts   │  │   History   │  │  (Monitoring)      │     │
│  │  (.h5/.pkl) │  │  (CSV/DB)   │  │                    │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Transaction Processing Flow

```
1. CLIENT REQUEST
   └── Transaction data (UPI IDs, Amount, Device, Location)
       │
       ▼
2. API GATEWAY
   └── Rate limiting, CORS, Authentication
       │
       ▼
3. REQUEST VALIDATION (Pydantic)
   └── Schema validation, Type checking
       │
       ▼
4. PREPROCESSING
   └── Feature extraction, Normalization
       │
       ▼
5. FEATURE STORE LOOKUP
   └── Retrieve user transaction history
       │
       ▼
6. MODEL INFERENCE (Parallel)
   ├── LSTM Model (Sequential patterns)
   │   └── User history → Pattern detection
   │       └── Score: 0.0 - 1.0
   │
   └── XGBoost Model (Feature analysis)
       └── Transaction features → Anomaly detection
           └── Score: 0.0 - 1.0
       │
       ▼
7. HYBRID SCORING
   └── Average: 0.5 × LSTM + 0.5 × XGBoost
       │
       ▼
8. DOMAIN RULE APPLICATION
   ├── Unknown Device Check
   ├── Velocity Check
   ├── Geolocation Analysis
   ├── Amount Threshold Check
   └── Time-based Rules
       │
       ▼
9. SHAP EXPLANATION
   └── Feature importance calculation
       │
       ▼
10. FINAL VERDICT
    ├── ALLOW (Score < 0.5)
    ├── FLAG (0.5 ≤ Score < 0.8)
    └── BLOCK (Score ≥ 0.8)
        │
        ▼
11. RESPONSE
    └── Risk score, Verdict, Factors
```

## Model Architecture

### Hybrid AI Approach

The system uses a 50/50 ensemble of two distinct model architectures:

#### A. XGBoost: Static Analysis (50% Weight)

| Aspect | Details |
|--------|---------|
| **Role** | Analyzes features of the current transaction in isolation |
| **Algorithm** | Gradient Boosting Decision Trees |
| **Input Features** | Amount, DeviceID, Geolocation, Time, etc. |
| **Strengths** | Handles missing values, efficient for real-time |
| **Explainability** | SHAP compatible |

**Architecture:**
```
Input Features
    ├── Numerical: Amount, Latitude, Longitude, Hour, etc.
    └── Categorical: SenderUPI, ReceiverUPI, DeviceID
        │
        ▼
    ┌───────────────────────┐
    │   XGBoost Classifier  │
    │   n_estimators: 100   │
    │   max_depth: 5       │
    │   learning_rate: 0.1│
    └───────────────────────┘
        │
        ▼
   Fraud Probability (0-1)
```

#### B. LSTM: Sequential Pattern Recognition (50% Weight)

| Aspect | Details |
|--------|---------|
| **Role** | Analyzes sequence of user's last N transactions |
| **Architecture** | Long Short-Term Memory Neural Network |
| **Lookback Window** | 10 transactions |
| **Input** | Temporal sequence of transaction features |
| **Strengths** | Detects velocity, behavioral shifts |

**Architecture:**
```
Transaction Sequence (N=10)
    │
    ┌────────────────────────────────────┐
    │          LSTM Architecture         │
    │  ┌────────────────────────────┐   │
    │  │ Input: (batch, 10, 8)       │   │
    │  │                             │   │
    │  │ Layer 1: LSTM(64)           │   │
    │  │ ├── return_sequences=True  │   │
    │  │ └── dropout: 0.2            │   │
    │  │                             │   │
    │  │ Layer 2: LSTM(32)           │   │
    │  │ └── dropout: 0.2           │   │
    │  │                             │   │
    │  │ Layer 3: Dense(1, sigmoid)  │   │
    │  └────────────────────────────┘   │
    └────────────────────────────────────┘
        │
        ▼
   Fraud Probability (0-1)
```

### Hybrid Scoring Formula

```
Final_Score = 0.5 × LSTM_Score + 0.5 × XGBoost_Score

If Final_Score > 0.8 → BLOCK
If Final_Score > 0.5 → FLAG
Else → ALLOW
```

## Feature Store Design

### Purpose

The Feature Store maintains real-time user transaction history for LSTM analysis.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Feature Store                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │                   Redis                          │   │
│  │  Key: upi:{user_id}:history                     │   │
│  │  Value: List of last N transactions             │   │
│  │  TTL: 30 days                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                   │                                    │
│         ┌─────────┴─────────┐                          │
│         ▼                   ▼                          │
│  ┌──────────────┐   ┌──────────────┐                  │
│  │  Velocity    │   │   User       │                  │
│  │  Tracking    │   │  Profiling   │                  │
│  └──────────────┘   └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

### Data Structure

```json
{
  "user_id": "user@upi",
  "transactions": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "amount": 500.0,
      "receiver": "merchant@upi",
      "device_id": "82:4e:8e:2a:9e:28",
      "location": {"lat": 12.97, "lng": 77.59}
    }
  ],
  "velocity": {
    "last_hour_count": 5,
    "last_24h_count": 15,
    "last_hour_amount": 25000.0
  }
}
```

## Domain Rules Engine

### Rule Hierarchy

| Priority | Rule | Condition | Score Impact |
|----------|------|-----------|--------------|
| 1 | High Velocity | > 5 txns/hour | +0.45 |
| 2 | Unknown Device | Device not in whitelist | +0.30-0.50 |
| 3 | High Amount + Unusual Hour | > ₹10k + 0-5 AM | +0.40 |
| 4 | Amount Threshold | > ₹50k | +0.35 |
| 5 | Impossible Travel | > 500 km in < 5 min | +0.50 |

### Rule Processing Logic

```python
# Pseudo-code for domain rule application
def apply_domain_rules(transaction, ai_score):
    final_score = ai_score
    
    # Check velocity
    if velocity > THRESHOLD:
        final_score = max(final_score, 0.85)
        factors["High Velocity"] = 0.45
    
    # Check device
    if not is_known_device(transaction.device_id):
        if ai_score > 0.4 or amount > HIGH_AMOUNT:
            final_score = max(final_score, 0.95)
            factors["Unknown Device + High Risk"] = 0.50
        else:
            final_score = max(final_score, 0.60)
            factors["New Device"] = 0.30
    
    # Check time + amount
    if amount > HIGH_AMOUNT and hour in UNUSUAL_HOURS:
        final_score = max(final_score, 0.60)
        factors["Unusual Hour + High Amount"] = 0.40
    
    return final_score
```

## Security Architecture

### API Security

| Layer | Implementation |
|-------|----------------|
| Rate Limiting | slowapi (10 req/min for /predict) |
| CORS | Configured allowed origins |
| Input Validation | Pydantic schemas |
| Model Security | Checksum validation |
| Logging | Structured JSON logs |

### Model Security

```
Model Loading Security Chain
    │
    ├── Checksum Validation
    │   └── SHA256 hash verification
    │
    ├── Secure Deserialization
    │   └── Restricted unpickling
    │
    ├── Model Signing
    │   └── Digital signature verification
    │
    └── Audit Logging
        └── All model loads logged
```

## Scalability Considerations

### Horizontal Scaling

```
                    ┌─────────────────────┐
                    │   Load Balancer     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │  API Server   │  │  API Server   │  │  API Server   │
      │    (8001)     │  │    (8002)     │  │    (8003)     │
      └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────┐
                    │   Shared Model      │
                    │   Artifacts         │
                    │   (NFS/S3)          │
                    └─────────────────────┘
```

### Recommended Scaling

| Component | Scaling Strategy |
|-----------|-----------------|
| API Servers | Stateless, auto-scaling behind LB |
| Redis | Cluster mode for high availability |
| Models | Shared read-only storage |
| Database | Connection pooling, read replicas |

## Technology Stack

### Backend

| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Primary language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pydantic | Data validation |
| TensorFlow 2.x | LSTM model training/inference |
| XGBoost 2.x | Gradient boosting |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Redis | Feature store |
| YAML | Configuration |
| pytest | Testing |

### Monitoring

| Technology | Purpose |
|------------|---------|
| Structured Logging | Request/response logging |
| Prometheus | Metrics collection |
| Grafana | Visualization |

## Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Latency | < 100ms | P95 |
| Model Inference | < 50ms | P95 |
| Throughput | 1000 TPS | Per server |
| Availability | 99.9% | Monthly SLA |

## Future Architecture Plans

### Roadmap

| Phase | Feature | Description |
|-------|---------|-------------|
| v2.0 | Kafka Integration | Real-time streaming |
| v2.0 | Kubernetes | Orchestration |
| v2.1 | Graph Neural Networks | Relationship analysis |
| v2.1 | Multi-cloud | Provider redundancy |
| v3.0 | Federated Learning | Privacy-preserving training |
