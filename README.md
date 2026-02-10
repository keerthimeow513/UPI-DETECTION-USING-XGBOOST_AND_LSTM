# UPI Fraud Detection System

A real-time hybrid AI-based fraud detection system for UPI (Unified Payments Interface) transactions using XGBoost and LSTM models with explainable AI capabilities.

## Overview

This project implements a sophisticated fraud detection system for UPI transactions in India. The system uses a hybrid approach combining:

- **LSTM (Long Short-Term Memory)**: Deep learning model for sequential pattern recognition
- **XGBoost**: Gradient boosting model for feature-based classification
- **Domain Rules**: Context-aware safety layer for enhanced security
- **SHAP Explainability**: Transparency into model decisions

## Features

- **Real-time fraud detection** with sub-second latency
- **Hybrid AI scoring** combining LSTM and XGBoost models
- **Domain rule enhancement** for account takeover protection
- **Explainable AI** using SHAP values
- **Interactive dashboard** with Streamlit
- **REST API** for integration with payment systems
- **Mock payment app** for testing and demonstration

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)
- 4GB RAM minimum (8GB recommended)
- 2GB disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd UPI_FRAUD_DETECTION
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate synthetic data** (optional)
   ```bash
   python utils/generate_data.py
   ```

5. **Train the models**
   ```bash
   python 03_training/train.py
   ```

### Running the Application

#### Start the API Server

**Linux/Mac:**
```bash
uvicorn 04_inference.api:app --reload
```

**Windows (PowerShell):**
```powershell
cd 04_inference
python -m uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

#### Launch the Dashboard

```bash
streamlit run 06_dashboard/app.py
```

Access the dashboard at `http://localhost:8501`

#### Test with Mock Payment App

```bash
python mock_payment_app.py
```

#### Run Verification Scenarios

```bash
python verify_scenarios.py
```

## Project Structure

```
UPI_FRAUD_DETECTION/
├── 01_data/
│   ├── raw/                    # Raw transaction data
│   └── processed/              # Processed training data
├── 02_models/
│   └── artifacts/              # Trained models and scalers
├── 03_training/                # Training scripts
│   └── train.py                # Model training pipeline
├── 04_inference/               # API and prediction service
│   ├── api.py                  # FastAPI server
│   ├── service.py              # Core fraud detection logic
│   └── schemas.py              # Pydantic schemas
├── utils/                      # Utility modules
│   ├── preprocessing.py        # Data preprocessing
│   ├── logger.py              # Logging utilities
│   ├── security.py            # Model security
│   ├── feature_store.py       # User history storage
│   └── generate_data.py       # Synthetic data generation
├── 05_dashboard/               # Streamlit dashboard
├── 06_notebooks/               # Jupyter notebooks
├── 07_configs/                 # Configuration files
│   └── config.yaml            # Main configuration
├── tests/                      # Unit and integration tests
├── docker-compose.yml         # Docker composition
├── Dockerfile                 # API container
├── Dockerfile.dashboard       # Dashboard container
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## API Documentation

### Base URL

Development: `http://localhost:8000`

Production: `https://api.yourdomain.com`

### Endpoints

#### Health Check

```http
GET /
```

**Response:**
```json
{
    "status": "online",
    "system": "UPI Fraud Shield",
    "environment": "development",
    "version": "1.0.0"
}
```

#### Predict Fraud

```http
POST /predict
Content-Type: application/json
```

**Request Body:**
```json
{
    "SenderUPI": "user@upi",
    "ReceiverUPI": "merchant@upi",
    "Amount": 5000.0,
    "DeviceID": "82:4e:8e:2a:9e:28",
    "Latitude": 12.97,
    "Longitude": 77.59,
    "Hour": 14,
    "DayOfWeek": 1,
    "DayOfMonth": 15,
    "TimeDiff": 3600,
    "AmountDiff": 1000
}
```

**Response:**
```json
{
    "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
    "risk_score": 0.75,
    "verdict": "BLOCK",
    "lstm_score": 0.72,
    "xgb_score": 0.78,
    "factors": {
        "Unknown Device": 0.35,
        "High Amount": 0.25,
        "Unusual Hour": 0.15
    }
}
```

## Model Performance

The hybrid model achieves:

| Metric | Score |
|--------|-------|
| Accuracy | 95%+ |
| Precision | 90%+ |
| Recall | 85%+ |
| F1 Score | 87%+ |
| ROC AUC | 95%+ |

## Security Features

1. **Device Recognition**: Detects unknown devices
2. **Geolocation Analysis**: Flags unusual locations
3. **Time-based Rules**: Detects suspicious hour patterns
4. **Amount Thresholds**: High-value transaction monitoring
5. **Velocity Detection**: Multiple transactions in short time
6. **Hybrid Scoring**: Combines ML with domain expertise
7. **Rate Limiting**: Prevents abuse of API endpoints
8. **Model Security**: Checksum validation for model files

## Configuration

Edit `07_configs/config.yaml` to customize:

- **Data paths**: Input/output file locations
- **Model parameters**: LSTM and XGBoost hyperparameters
- **Feature engineering**: Numerical and categorical features
- **API settings**: Host and port configuration
- **Security settings**: Safe devices and risk thresholds

## Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Required variables:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Database (optional)
DATABASE_URL=sqlite:///./upi_fraud.db

# Environment
ENVIRONMENT=development
```

## Testing

### Run all tests

```bash
python -m pytest tests/ -v
```

### Run specific test

```bash
python -m pytest tests/test_project.py -v
```

### Run with coverage

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Run verification scenarios

```bash
python verify_scenarios.py
```

## Docker Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

### Building individually

```bash
# Build API
docker build -t upi-fraud-api .

# Build Dashboard
docker build -f Dockerfile.dashboard -t upi-fraud-dashboard .
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- XGBoost library for gradient boosting
- TensorFlow/Keras for deep learning
- SHAP for model explainability
- FastAPI for high-performance API
- Streamlit for interactive dashboard

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/yourusername/UPI_FRAUD_DETECTION/issues).

## Roadmap

- [ ] Redis integration for feature store
- [ ] Kubernetes deployment
- [ ] Real-time streaming with Kafka
- [ ] Advanced geofencing
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Enhanced reporting analytics
