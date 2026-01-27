# UPI Fraud Detection System: Technical Documentation

## 1. Project Overview
This project implements a **Hybrid Explainable AI (XAI)** system designed to detect fraudulent UPI (Unified Payments Interface) transactions in real-time. It combines traditional machine learning with deep learning to capture both static transaction anomalies and temporal behavioral patterns.

### Why Hybrid?
*   **XGBoost (Gradient Boosting):** Excellent at identifying fraud based on specific transaction attributes (e.g., unusually high amount, unknown device, odd hour).
*   **LSTM (Long Short-Term Memory):** A Recurrent Neural Network (RNN) that analyzes a sequence of the last 10 transactions to detect shifts in user behavior (e.g., a sudden burst of transactions after months of inactivity).
*   **Explainability (SHAP):** Provides transparency by showing exactly which features contributed to a "Fraud" verdict, which is critical for banking compliance and user trust.

---

## 2. Directory Structure & File Roles

| Path | File | Description |
| :--- | :--- | :--- |
| `01_data/` | `raw/upi_transactions.csv` | The dataset containing transaction history, amounts, and fraud labels. |
| `02_models/` | `artifacts/` | Contains the trained models (`.h5`, `.pkl`) and preprocessing tools (`scaler.pkl`). |
| `03_training/` | `train.py` | The automated pipeline that reads data, engineers features, and trains the hybrid models. |
| `04_inference/` | `api.py` | A FastAPI server that exposes a `/predict` endpoint for real-time integration. |
| `04_inference/` | `service.py` | The core engine that runs models, applies domain rules, and generates SHAP explanations. |
| `06_dashboard/` | `app.py` | A Streamlit-based web interface for monitoring transactions and testing the AI live. |
| `07_configs/` | `config.yaml` | The central configuration file for paths, model hyperparameters, and feature lists. |
| `utils/` | `preprocessing.py` | Logic for converting raw transaction data into numerical formats suitable for AI. |
| `utils/` | `logger.py` | Standardized logging to track system performance and fraud alerts. |
| `/` | `mock_payment_app.py` | A simulation tool that acts like a mobile app to test the system under normal and attack scenarios. |
| `/` | `verify_scenarios.py` | A verification script to test the 4 key business scenarios (Safe, New Device, Late Night, Hacker). |

---

## 3. Business Logic: Safe vs. Hacker Scenarios

The system uses a **Graduated Response** strategy to ensure that genuine users are not blocked while hackers are stopped.

| Scenario | Input Pattern | Result | Business Rationale |
| :--- | :--- | :--- | :--- |
| **The Regular User** | Registered Device, ₹1,200, 2 PM | **ALLOW** | Standard behavior on a known device is trusted. |
| **The New Phone User**| **New Device**, ₹1,200, 2 PM | **FLAG (OTP)** | A new device is a minor risk; we challenge with an OTP. |
| **Late Night Shopper** | Registered Device, **₹15,000**, **3 AM** | **FLAG (OTP)** | Unusual hours and high amounts trigger safety checks. |
| **The Hacker** | **New Device**, **₹45,000**, **3 AM** | **BLOCK** | Multiple risk factors combined indicate high fraud risk. |

---

## 4. How the System Works (The Lifecycle)

### Step 1: Data Engineering
Raw transactions (Amount, Timestamp, GPS) are transformed into:
*   **Temporal Features:** Hour of day, Day of week.
*   **Lag Features:** Time elapsed since the last transaction, difference in amount from the previous transaction.

### Step 2: Training
*   The system handles **Class Imbalance** (fraud is rare) using `scale_pos_weight` in XGBoost and `class_weight` in Keras.
*   It saves "Artifacts" (Scalers and Encoders) to ensure the exact same transformations are used during live prediction.

### Step 3: Real-Time Inference
1.  A transaction comes in via the **API**.
2.  The **Service** fetches (or mocks) the user's history to create a 10-step sequence for the LSTM.
3.  **XGBoost** predicts a score. **LSTM** predicts a score.
4.  **Hybrid Logic:** The scores are averaged.
5.  **Domain Rules:** Additional logic checks for unknown devices and unusual patterns to refine the verdict.
6.  **SHAP** analyzes the XGBoost model to explain the verdict.

---

## 5. How to Upgrade (The Roadmap)

### Level 1: Real-Time History (Database Integration)
Currently, history is "mocked" in `service.py`. 
*   **Upgrade:** Connect to a Redis or SQL database.

### Level 2: Geofencing & Velocity Rules
Detect "Impossible Travel".
*   **Upgrade:** Calculate distance between the current GPS coordinates and the last known transaction GPS coordinates.

### Level 3: Model Retraining (CI/CD)
*   **Upgrade:** Automate `train.py` to run weekly on new data and auto-deploy the new model if its F1-Score is higher than the current one.

### Level 4: Dockerization
Run the whole system anywhere with one command.
*   **Upgrade:** Use a `Dockerfile` to containerize the application.
