import sys # Import system library for path manipulation
import os # Import OS library for managing environment variables and paths

# Add project root and inference folder to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, '04_inference'))

# Disable GPU for inference to avoid conflicts and ensure it runs on standard CPU servers
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import streamlit as st # Import Streamlit for building the web interface
import pandas as pd # Import pandas for data manipulation and displaying tables
import numpy as np # Import numpy for array and matrix operations
import shap # Import SHAP for generating explainability charts
import joblib # Import joblib for loading serialized model files
import matplotlib.pyplot as plt # Import Matplotlib for basic plotting
import seaborn as sns # Import Seaborn for statistical data visualization
import yaml # Import yaml for reading configuration files
from datetime import datetime # Import datetime for timestamping new entries
from utils.preprocessing import Preprocessor # Import our custom data transformation utility
from service import FraudDetectionService # Import the core AI service

# Set Page Configuration for the Streamlit web app
st.set_page_config(
    page_title="UPI Fraud Detection System", # Title of the browser tab
    page_icon="[Shield]", # Favicon for the browser tab
    layout="wide", # Use the full width of the screen
    initial_sidebar_state="expanded" # Keep the sidebar open by default
)

# Initialize Session State for tracking new predictions live
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Load Configuration from the YAML file
with open('07_configs/config.yaml', 'r') as f: # Open the file in read mode
    config = yaml.safe_load(f) # Convert YAML content to a Python dictionary

# Load AI Assets and cache them to prevent reloading on every user click
@st.cache_resource # Tell Streamlit to keep these objects in memory
def load_assets(): # Function to load models and the preprocessor
    print("Loading AI service and assets...") # Debug message in terminal
    # Ensure the path is absolute for the service
    cfg_path = os.path.join(project_root, '07_configs', 'config.yaml')
    service = FraudDetectionService(cfg_path) # Initialize the full AI service (includes models and preprocessor)
    return service

try: # Attempt to load the assets and handle errors if files are missing
    service = load_assets()
except Exception as e: # Catch any loading errors
    st.error(f"Error loading AI Service: {e}") # Show a red error box in the UI
    st.stop() # Stop the execution of the app

# Sidebar UI Elements
st.sidebar.title("UPI Shield") # Sidebar title
st.sidebar.markdown("Hybrid Explainable AI-Based Real-Time UPI Fraud Detection") # Description text

# Navigation menu in the sidebar
menu = st.sidebar.radio("Navigation", ["Dashboard", "Real-Time Prediction", "Model Performance"])

if menu == "Dashboard": # Logic for the main data overview page
    st.title("User Transaction Dashboard") # Page heading
    
    # Load raw data for display on the dashboard
    df_raw = pd.read_csv('01_data/raw/upi_transactions.csv') # Read the transaction CSV
    df_raw['Timestamp'] = pd.to_datetime(df_raw['Timestamp']) # Convert timestamp strings to datetime objects
    
    # Combine CSV data with session history (Live updates)
    if st.session_state['history']:
        df_history = pd.DataFrame(st.session_state['history'])
        # Map verdict to IsFraud for charts
        df_history['IsFraud'] = df_history['verdict'].apply(lambda x: 1 if x == "BLOCK" else 0)
        # Ensure correct column order and names to match CSV as much as possible
        df = pd.concat([df_raw, df_history], ignore_index=True)
    else:
        df = df_raw
    
    # Calculate Key Performance Indicators (KPIs)
    total_trans = len(df) # Total count of transactions
    fraud_trans = df['IsFraud'].sum() # Count of fraudulent transactions
    total_amt = df['Amount'].sum() # Sum of all transaction values
    fraud_amt = df[df['IsFraud'] == 1]['Amount'].sum() # Sum of fraudulent transaction values
    
    # Display metrics in 4 columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", f"{total_trans:,}") # Display total count
    col2.metric("Fraud Cases Detected", f"{fraud_trans:,}") # Display fraud count
    col3.metric("Total Volume", f"₹{total_amt:,.2f}") # Display total value formatted as currency
    col4.metric("Fraud Volume", f"₹{fraud_amt:,.2f}") # Display fraud value formatted as currency
    
    # Show the 10 most recent transactions (Including live ones)
    st.subheader("Recent Transactions (Live Feed)")
    display_cols = ['Timestamp', 'SenderUPI', 'ReceiverUPI', 'Amount', 'DeviceID', 'IsFraud']
    st.dataframe(df.sort_values(by='Timestamp', ascending=False)[display_cols].head(10)) # Display interactive table
    
    # Data Visualization section
    st.subheader("Transaction Analysis")
    c1, c2 = st.columns(2) # Create two columns for charts
    
    with c1: # First chart: Fraud count comparison
        st.write("Fraud vs Normal Transactions") # Chart title
        fig, ax = plt.subplots() # Create a figure
        sns.countplot(x='IsFraud', data=df, ax=ax, palette=['#4CAF50', '#F44336']) # Plot bar chart
        ax.set_xticklabels(['Normal', 'Fraud']) # Label the bars
        st.pyplot(fig) # Render the plot in Streamlit
        
    with c2: # Second chart: Distribution of transaction amounts
        st.write("Transaction Amount Distribution (Log Scale)") # Chart title
        fig, ax = plt.subplots() # Create a figure
        sns.histplot(df['Amount'], bins=50, log_scale=True, ax=ax) # Plot histogram on log scale
        st.pyplot(fig) # Render the plot in Streamlit

elif menu == "Real-Time Prediction": # Logic for the interactive testing page
    st.title("Real-Time Fraud Detection") # Page heading
    st.markdown("Enter transaction details to assess fraud risk. Unknown devices will trigger immediate blocking.") # Instructional text
    
    # Form for user input
    with st.form("prediction_form"): # Wrap inputs in a form to prevent refresh on every keypress
        col1, col2 = st.columns(2) # Two columns for input fields
        
        with col1: # Left column inputs
            sender_upi = st.text_input("Sender UPI ID", "example@upi") # User's UPI
            receiver_upi = st.text_input("Receiver UPI ID", "merchant@upi") # Receiver's UPI
            amount = st.number_input("Amount (₹)", min_value=0.0, value=1000.0) # Transaction amount
            device_id = st.text_input("Device ID (MAC)", "00:00:00:00:00:00") # Device hardware ID
            
        with col2: # Right column inputs
            hour = st.slider("Hour of Day", 0, 23, 12) # Time of transaction
            day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 0) # Day of the week
            lat = st.number_input("Latitude", value=28.6139) # GPS Latitude
            long = st.number_input("Longitude", value=77.2090) # GPS Longitude
            
        # Submit button to trigger the analysis
        submitted = st.form_submit_button("Analyze Transaction")
        
    if submitted: # If the button was clicked
        try: # Run the prediction pipeline
            # Construct input dictionary to match the service's expected format
            data = {
                "SenderUPI": sender_upi,
                "ReceiverUPI": receiver_upi,
                "Amount": amount,
                "DeviceID": device_id,
                "Latitude": lat,
                "Longitude": long,
                "Hour": hour,
                "DayOfWeek": day_of_week,
                "DayOfMonth": datetime.now().day, # Use current day
                "TimeDiff": 0, # Mock constant for demo
                "AmountDiff": 0 # Mock constant for demo
            }
            
            # Use the core service for prediction (This includes Domain Rules like MAC check)
            result = service.predict(data)
            
            # Store result in session history for Dashboard update
            new_entry = data.copy()
            new_entry['Timestamp'] = datetime.now()
            new_entry['verdict'] = result['verdict']
            new_entry['risk_score'] = result['risk_score']
            st.session_state['history'].append(new_entry)
            
            # Display Results in the UI
            st.divider() # Horizontal line separator
            c1, c2, c3 = st.columns(3) # Three columns for individual scores
            c1.metric("LSTM Risk Score", f"{result['lstm_score']:.4f}") # Show raw LSTM score
            c2.metric("XGBoost Risk Score", f"{result['xgb_score']:.4f}") # Show raw XGBoost score
            c3.metric("Final Risk Score", f"{result['risk_score']:.4f}") # Show combined score
            
            # Display a success/error box based on the verdict
            if result['verdict'] == "BLOCK": # Threshold for fraud detection
                st.error(f"BLOCK: High Fraud Risk Detected! (Verdict: {result['verdict']})") # Red alert
            elif result['verdict'] == "FLAG":
                st.warning(f"FLAG: Suspicious Activity Detected. (Verdict: {result['verdict']})") # Yellow warning
            else:
                st.success(f"ALLOW: Transaction appears Safe. (Verdict: {result['verdict']})") # Green success
                
            # Explainability Section (XAI)
            st.subheader("Explainability (XAI)") # Section title
            
            # Re-calculate SHAP values for display
            feature_vector = service.preprocessor.transform_single(data)
            xgb_input = feature_vector.reshape(1, -1)
            shap_values = service.explainer.shap_values(xgb_input)
            
            fig_shap = plt.figure(figsize=(10, 6)) # Create a matplotlib figure
            # Generate a bar plot showing which features increased or decreased risk the most
            shap.summary_plot(shap_values, xgb_input, feature_names=service.preprocessor.feature_names, plot_type="bar", show=False)
            st.pyplot(fig_shap) # Render the SHAP plot in Streamlit

        except Exception as e: # Handle any errors during prediction
            st.error(f"Error during prediction: {e}")

elif menu == "Model Performance": # Logic for the metrics page
    st.title("Model Performance Metrics") # Page heading
    
    try: # Load and display the metrics saved during the training phase
        import json # Import json to read the metrics file
        with open('02_models/artifacts/metrics.json', 'r') as f: # Open the file
            metrics = json.load(f) # Load JSON content
            
        st.json(metrics) # Display the metrics as a formatted JSON object in the UI
        
    except: # Handle case where training hasn't been run yet
        st.warning("Metrics file not found. Run training script first.") # Warning message
