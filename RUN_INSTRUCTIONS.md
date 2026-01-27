# UPI Fraud Detection System: Execution Guide

This guide explains how to run the project and what to expect from each component.

## 1. Prerequisites
Ensure you are using the correct Python environment (conda environment `/home/akarsh/miniconda3/envs/phishing-detection-mllm` is recommended).

## 2. Step-by-Step Execution

### Step A: Training (Optional)
If you need to regenerate the models or if you change the dataset:
```bash
python 03_training/train.py
```
*What happens:* The system processes the raw CSV data, engineers temporal and lag features, and trains a hybrid ensemble of XGBoost and LSTM models. Performance metrics are saved to `02_models/artifacts/metrics.json`.

### Step B: Start the Inference API
This is the "brain" of the system that calculates fraud risk in real-time.
```bash
uvicorn 04_inference.api:app --host 0.0.0.0 --port 8000
```
*What happens:* The server loads the trained models and exposes a POST endpoint at `/predict`. It listens for transaction data and returns a risk score, a verdict (ALLOW/FLAG/BLOCK), and the top factors contributing to the score.

### Step C: Run the Payment Simulator
Use this to test the system live.
```bash
python mock_payment_app.py
```
*What happens:* An interactive menu allows you to simulate:
1. **Normal Payment:** Uses a registered device and home location.
2. **Hacker Attack:** Uses an unknown device and distant GPS coordinates.
*Result:* The app communicates with the API and displays the bank's decision.

### Step D: View the Dashboard
To see a visual summary of transactions and system performance:
```bash
streamlit run 06_dashboard/app.py
```
*What happens:* A web-based dashboard opens showing:
- Transaction volume and fraud rates.
- A real-time prediction form for manual testing.
- Model explainability (XAI) charts showing feature importance.

---

## 3. What to Expect
- **Accuracy:** The system is designed to catch 95%+ of typical fraud patterns.
- **Explainability:** For every blocked transaction, you will see exactly why (e.g., "Unknown Device" or "Unusual Amount").
- **Security:** The system uses a hybrid approach where AI scores are combined with hard "Domain Rules" for maximum safety.
