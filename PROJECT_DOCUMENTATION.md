# UPI Fraud Detection System: Technical Documentation

## 1. Project Overview
This project implements a **Hybrid Explainable AI (XAI)** system designed to detect fraudulent UPI (Unified Payments Interface) transactions in real-time. It combines traditional machine learning with deep learning to capture both static transaction anomalies and temporal behavioral patterns.

---

## 2. Technical Architecture: The Hybrid Approach
The system uses a 50/50 ensemble of two distinct model architectures. This "dual-lens" approach is used because UPI fraud typically manifests in two ways: immediate anomalies and behavioral shifts.

### A. XGBoost: The Static Snapshot (50% Weight)
*   **Role:** Analyzes the features of the *current* transaction in isolation.
*   **Why XGBoost?** It is the state-of-the-art for tabular (structured) data. It handles missing values well and is computationally efficient for real-time APIs.
*   **Explainability:** We use XGBoost because it is compatible with **SHAP (SHapley Additive Explanations)**. In banking, a "Black Box" is not allowed; SHAP allows us to provide a human-readable reason (e.g., "Amount is too high") for every decision.
*   **What it catches:** "Point Anomalies" like an unrecognized device or an unusually large transaction amount.

### B. LSTM (Long Short-Term Memory): The Behavioral Story (50% Weight)
*   **Role:** Analyzes the sequence of the user's last 10 transactions.
*   **Why LSTM?** Standard models are "forgetful"—they treat every transaction as if it's the user's first. LSTM is a Recurrent Neural Network (RNN) that maintains an internal "memory" of past events.
*   **What it catches:** "Pattern Anomalies" such as a sudden burst of activity (e.g., 10 transactions in 5 minutes) from an account that is usually dormant. It detects the *velocity* and *rhythm* of fraud.

### C. Why the 50/50 Weighting?
We give equal weight to both models to ensure a **Balanced Verdict**. 
*   If we relied only on XGBoost, we would miss "Smurfing" attacks (many small, normal-looking transactions that only look suspicious when viewed as a sequence).
*   If we relied only on LSTM, we would miss "One-Shot" attacks (a single massive transaction that is a clear anomaly but doesn't fit a temporal pattern yet).
*   **Result:** A transaction is only fully "Trusted" (ALLOW) if it looks safe as a single event AND fits the user's historical story.

---

## 3. Business Logic: Safe vs. Hacker Scenarios

The system uses a **Graduated Response** strategy to balance security with user experience.

| Scenario | Input Pattern | Result | Business Rationale |
| :--- | :--- | :--- | :--- |
| **The Regular User** | Registered Device, < ₹10k, Day | **ALLOW** | Known user, typical behavior. Trusted. |
| **The New Phone User**| **New Device**, < ₹10k, Day | **FLAG (OTP)** | Minor risk (New Hardware). Needs verification. |
| **Late Night Shopper** | Registered Device, **> ₹10k**, **Night** | **FLAG (OTP)** | Unusual hour for high spend. Safety check. |
| **The Hacker** | **New Device**, **> ₹10k**, **Night** | **BLOCK** | High-risk device + high-risk behavior. Stopped. |

---

## 4. Directory Structure & File Roles

| Path | File | Description |
| :--- | :--- | :--- |
| `01_data/` | `raw/upi_transactions.csv` | The dataset containing transaction history and fraud labels. |
| `02_models/` | `artifacts/` | Trained model files (`.h5`, `.pkl`) and scalers. |
| `03_training/` | `train.py` | The pipeline that trains the XGBoost and LSTM models. |
| `04_inference/` | `api.py` | FastAPI server for real-time integration. |
| `04_inference/` | `service.py` | The core engine implementing the hybrid logic and domain rules. |
| `06_dashboard/` | `app.py` | Streamlit-based monitoring and testing interface. |
| `07_configs/` | `config.yaml` | Hyperparameters and path settings. |
| `utils/` | `preprocessing.py` | Logic for feature engineering and data scaling. |
| `/` | `verify_scenarios.py` | Automated test script for the 4 key business cases. |

---

## 5. How to Upgrade (The Roadmap)
1.  **Database Integration:** Replace "Mocked" history with a real Redis Feature Store.
2.  **Geofencing:** Add rules to detect "Impossible Travel" between transaction GPS points.
3.  **CI/CD:** Automate model retraining when new fraud patterns are detected in production.
