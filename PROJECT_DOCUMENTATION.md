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

---

## 3. How the System Works (The Lifecycle)

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
4.  **Hybrid Logic:** The scores are averaged. If a **Domain Rule** is triggered (e.g., Unknown Device ID), the score is manually boosted to 0.95 for safety.
5.  **SHAP** analyzes the XGBoost model to explain the verdict.

---

## 4. How to Upgrade (The Roadmap)

### Level 1: Real-Time History (Database Integration)
Currently, history is "mocked" in `service.py`. 
*   **Upgrade:** Connect to a Redis or SQL database.
*   **Code Example:**
    ```python
    # In service.py
    def get_user_history(user_id):
        return db.query("SELECT * FROM transactions WHERE sender = ? LIMIT 10", user_id)
    ```

### Level 2: Geofencing & Velocity Rules
Detect "Impossible Travel".
*   **Upgrade:** Calculate distance between the current GPS coordinates and the last known transaction GPS coordinates.
*   **Example:** If the distance is > 500km and the time difference is < 30 mins, automatically `BLOCK`.

### Level 3: Model Retraining (CI/CD)
*   **Upgrade:** Automate `train.py` to run weekly on new data and auto-deploy the new model if its F1-Score is higher than the current one.

### Level 4: Dockerization
Run the whole system anywhere with one command.
*   **Upgrade:** Create a `Dockerfile`:
    ```dockerfile
    FROM python:3.9
    COPY . /app
    RUN pip install -r requirements.txt
    CMD ["uvicorn", "04_inference.api:app", "--host", "0.0.0.0"]
    ```
