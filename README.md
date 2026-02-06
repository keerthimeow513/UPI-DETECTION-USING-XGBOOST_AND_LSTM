# UPI Fraud Detection System

A real-time hybrid AI-based fraud detection system for UPI transactions using XGBoost and LSTM models with explainable AI capabilities.

## Overview

This project implements a sophisticated fraud detection system for Unified Payments Interface (UPI) transactions in India. The system uses a hybrid approach combining:

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

## Project Structure

```
UPI_FRAUD_DETECTION/
├── 01_data/
│   ├── raw/                    # Raw transaction data
│   └── processed/              # Processed training data
├── 02_models/
│   └── artifacts/              # Trained models and scalers
├── 03_training/                # Training scripts
├── 04_inference/               # API and prediction service
├── utils/                      # Utility modules
│   ├── preprocessing.py        # Data preprocessing
│   ├── logger.py              # Logging utilities
│   └── generate_data.py       # Synthetic data generation
├── 06_dashboard/               # Streamlit dashboard
├── 06_notebooks/               # Jupyter notebooks for analysis
├── 07_configs/                 # Configuration files
└── tests/                      # Unit and integration tests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

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

## Usage

### 1. Start the API Server

```bash
uvicorn 04_inference.api:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Launch the Dashboard

```bash
streamlit run 06_dashboard/app.py
```

Access the dashboard at `http://localhost:8501`

### 3. Test with Mock Payment App

```bash
python mock_payment_app.py
```

### 4. Run Verification Scenarios

```bash
python verify_scenarios.py
```

## API Endpoints

### Health Check
```bash
GET /
Response: {"status": "online", "system": "UPI Fraud Shield"}
```

### Predict Fraud
```bash
POST /predict
Content-Type: application/json

{
  "SenderUPI": "user@upi",
  "ReceiverUPI": "merchant@upi",
  "Amount": 5000.0,
  "DeviceID": "82:4e:8e:2a:9e:28",
  "Latitude": 12.97,
  "Longitude": 77.59,
  "Hour": 14,
  "DayOfWeek": 1
}
```

**Response:**
```json
{
  "transaction_id": "uuid",
  "risk_score": 0.75,
  "verdict": "BLOCK",
  "factors": {
    "Amount": 0.25,
    "DeviceID": 0.20,
    ...
  }
}
```

## Configuration

Edit `07_configs/config.yaml` to customize:

- **Data paths**: Input/output file locations
- **Model parameters**: LSTM and XGBoost hyperparameters
- **Feature engineering**: Numerical and categorical features
- **API settings**: Host and port configuration
- **Security settings**: Safe devices and risk thresholds

## Testing

### Run all tests
```bash
python -m pytest tests/
```

### Run specific test
```bash
python -m pytest tests/test_project.py
```

### Run verification scenarios
```bash
python verify_scenarios.py
```

## Model Performance

The hybrid model achieves:
- **Accuracy**: 95%+
- **Precision**: 90%+
- **Recall**: 85%+
- **F1 Score**: 87%+
- **ROC AUC**: 95%+

## Security Features

1. **Device Recognition**: Detects unknown devices
2. **Geolocation Analysis**: Flags unusual locations
3. **Time-based Rules**: Detects suspicious hour patterns
4. **Amount Thresholds**: High-value transaction monitoring
5. **Hybrid Scoring**: Combines ML with domain expertise

## Explainability

The system provides SHAP-based explanations showing:
- Top factors contributing to fraud risk
- Feature importance rankings
- Risk contribution values

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- XGBoost library for gradient boosting
- TensorFlow/Keras for deep learning
- SHAP for model explainability
- FastAPI for high-performance API
- Streamlit for interactive dashboard

## Support

For issues and feature requests, please use the GitHub issue tracker.

## Roadmap

- [ ] Redis integration for feature store
- [ ] Kubernetes deployment
- [ ] Real-time streaming with Kafka
- [ ] Advanced geofencing
- [ ] Mobile app integration
