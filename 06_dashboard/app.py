import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable GPU for inference to avoid conflicts
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import tensorflow as tf
import shap
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
from utils.preprocessing import Preprocessor

# Set Page Config
st.set_page_config(
    page_title="UPI Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Config
with open('07_configs/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Load Assets
@st.cache_resource
def load_assets():
    print("Loading models and data...")
    lstm_model = tf.keras.models.load_model('02_models/artifacts/lstm_model.h5')
    xgb_model = joblib.load('02_models/artifacts/xgb_model.pkl')
    
    preprocessor = Preprocessor('07_configs/config.yaml')
    preprocessor.load_artifacts()
    
    return lstm_model, xgb_model, preprocessor

try:
    lstm_model, xgb_model, preprocessor = load_assets()
except Exception as e:
    st.error(f"Error loading assets: {e}")
    st.stop()

# Sidebar
st.sidebar.title("🛡️ UPI Shield")
st.sidebar.markdown("Hybrid Explainable AI-Based Real-Time UPI Fraud Detection")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Real-Time Prediction", "Model Performance"])

if menu == "Dashboard":
    st.title("User Transaction Dashboard")
    
    # Load raw data for display
    df = pd.read_csv('01_data/raw/upi_transactions.csv')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Metrics
    total_trans = len(df)
    fraud_trans = df['IsFraud'].sum()
    total_amt = df['Amount'].sum()
    fraud_amt = df[df['IsFraud'] == 1]['Amount'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", f"{total_trans:,}")
    col2.metric("Fraud Cases Detected", f"{fraud_trans:,}")
    col3.metric("Total Volume", f"₹{total_amt:,.2f}")
    col4.metric("Fraud Volume", f"₹{fraud_amt:,.2f}")
    
    # Recent Transactions
    st.subheader("Recent Transactions")
    st.dataframe(df.sort_values(by='Timestamp', ascending=False).head(10))
    
    # Visuals
    st.subheader("Transaction Analysis")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("Fraud vs Normal Transactions")
        fig, ax = plt.subplots()
        sns.countplot(x='IsFraud', data=df, ax=ax, palette=['#4CAF50', '#F44336'])
        ax.set_xticklabels(['Normal', 'Fraud'])
        st.pyplot(fig)
        
    with c2:
        st.write("Transaction Amount Distribution (Log Scale)")
        fig, ax = plt.subplots()
        sns.histplot(df['Amount'], bins=50, log_scale=True, ax=ax)
        st.pyplot(fig)

elif menu == "Real-Time Prediction":
    st.title("Real-Time Fraud Detection")
    st.markdown("Enter transaction details to assess fraud risk.")
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sender_upi = st.text_input("Sender UPI ID", "example@upi")
            receiver_upi = st.text_input("Receiver UPI ID", "merchant@upi")
            amount = st.number_input("Amount (₹)", min_value=0.0, value=1000.0)
            device_id = st.text_input("Device ID (MAC)", "00:00:00:00:00:00")
            
        with col2:
            hour = st.slider("Hour of Day", 0, 23, 12)
            day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 0)
            lat = st.number_input("Latitude", value=28.6139)
            long = st.number_input("Longitude", value=77.2090)
            
        # Simplified inputs for demo
        submitted = st.form_submit_button("Analyze Transaction")
        
    if submitted:
        try:
            # Construct Input Dict
            data = {
                "SenderUPI": sender_upi,
                "ReceiverUPI": receiver_upi,
                "Amount": amount,
                "DeviceID": device_id,
                "Latitude": lat,
                "Longitude": long,
                "Hour": hour,
                "DayOfWeek": day_of_week,
                "DayOfMonth": 1, # Mock
                "TimeDiff": 0, # Mock
                "AmountDiff": 0 # Mock
            }
            
            # Preprocess
            feature_vector = preprocessor.transform_single(data)
            
            # Reshape
            xgb_input = feature_vector.reshape(1, -1)
            lstm_input = np.tile(feature_vector, (1, 10, 1))
            
            # Predict
            lstm_prob = lstm_model.predict(lstm_input)[0][0]
            xgb_prob = xgb_model.predict_proba(xgb_input)[0][1]
            hybrid_score = 0.5 * lstm_prob + 0.5 * xgb_prob
            
            # Display Result
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("LSTM Risk Score", f"{lstm_prob:.4f}")
            c2.metric("XGBoost Risk Score", f"{xgb_prob:.4f}")
            c3.metric("Hybrid Risk Score", f"{hybrid_score:.4f}")
            
            if hybrid_score > 0.5:
                st.error("🚨 HIGH RISK: Potential Fraud Detected!")
            else:
                st.success("✅ LOW RISK: Transaction appears Safe.")
                
            # Explainability
            st.subheader("Explainability (XAI)")
            explainer = shap.TreeExplainer(xgb_model)
            shap_values = explainer.shap_values(xgb_input)
            
            fig_shap = plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, xgb_input, feature_names=preprocessor.feature_names, plot_type="bar", show=False)
            st.pyplot(fig_shap)

        except Exception as e:
            st.error(f"Error during prediction: {e}")

elif menu == "Model Performance":
    st.title("Model Performance Metrics")
    
    try:
        import json
        with open('02_models/artifacts/metrics.json', 'r') as f:
            metrics = json.load(f)
            
        st.json(metrics)
        
    except:
        st.warning("Metrics file not found. Run training script first.")
