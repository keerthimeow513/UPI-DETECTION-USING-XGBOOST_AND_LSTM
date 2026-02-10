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
menu = st.sidebar.radio("Navigation", ["Dashboard", "Real-Time Prediction", "Model Performance", "Admin Panel"])

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

elif menu == "Admin Panel": # Admin Panel for system configuration
    st.title("Admin Panel")
    
    # Initialize session state for admin configurations
    if 'whitelisted_devices' not in st.session_state:
        st.session_state['whitelisted_devices'] = pd.DataFrame({
            'DeviceID': ['AA:BB:CC:DD:EE:01', 'AA:BB:CC:DD:EE:02', 'AA:BB:CC:DD:EE:03'],
            'UsageCount': [15, 8, 3],
            'LastSeen': ['2026-02-10 10:30:00', '2026-02-09 14:22:00', '2026-02-08 09:15:00'],
            'Status': ['Active', 'Active', 'Active']
        })
    
    if 'risk_thresholds' not in st.session_state:
        st.session_state['risk_thresholds'] = {
            'allow_threshold': 0.3,
            'flag_threshold': 0.5,
            'block_threshold': 0.8,
            'amount_high': 10000,
            'amount_critical': 50000,
            'unusual_hour_start': 0,
            'unusual_hour_end': 5
        }
    
    if 'audit_logs' not in st.session_state:
        st.session_state['audit_logs'] = pd.DataFrame({
            'TransactionID': ['TXN001', 'TXN002', 'TXN003', 'TXN004', 'TXN005'],
            'Timestamp': ['2026-02-10 10:30:00', '2026-02-10 09:15:00', '2026-02-09 22:45:00', 
                         '2026-02-09 03:20:00', '2026-02-08 14:00:00'],
            'SenderUPI': ['user1@upi', 'user2@upi', 'user3@upi', 'user4@upi', 'user5@upi'],
            'Amount': [1500.0, 25000.0, 800.0, 55000.0, 500.0],
            'RiskScore': [0.85, 0.72, 0.55, 0.91, 0.48],
            'Verdict': ['BLOCK', 'BLOCK', 'FLAG', 'BLOCK', 'FLAG'],
            'Reason': ['High risk score', 'High amount', 'Unusual hour', 'Critical amount + unusual hour', 'Device unknown']
        })
    
    tab1, tab2, tab3 = st.tabs(["Device Management", "Risk Configuration", "Audit Logs"])
    
    with tab1:
        st.subheader("Known Safe Devices")
        st.markdown("Manage devices that are whitelisted for transactions.")
        
        # Display device statistics
        device_df = st.session_state['whitelisted_devices']
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        col_stats1.metric("Total Whitelisted Devices", len(device_df))
        col_stats2.metric("Total Usage Count", device_df['UsageCount'].sum())
        col_stats3.metric("Active Devices", len(device_df[device_df['Status'] == 'Active']))
        
        st.divider()
        
        # Add new device form
        with st.expander("Add New Device to Whitelist"):
            new_device_id = st.text_input("Device ID (MAC Address)", placeholder="AA:BB:CC:DD:EE:FF")
            if st.button("Add Device"):
                if new_device_id and new_device_id not in device_df['DeviceID'].values:
                    new_row = pd.DataFrame({
                        'DeviceID': [new_device_id],
                        'UsageCount': [0],
                        'LastSeen': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                        'Status': ['Active']
                    })
                    st.session_state['whitelisted_devices'] = pd.concat([device_df, new_row], ignore_index=True)
                    st.success(f"Device {new_device_id} added to whitelist!")
                    st.rerun()
                elif new_device_id in device_df['DeviceID'].values:
                    st.error("Device already exists in whitelist!")
                else:
                    st.error("Please enter a valid Device ID!")
        
        # Editable device list
        st.subheader("Whitelisted Devices List")
        edited_df = st.data_editor(
            device_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                'DeviceID': st.column_config.TextColumn('Device ID', disabled=True),
                'UsageCount': st.column_config.NumberColumn('Usage Count', min_value=0),
                'LastSeen': st.column_config.DatetimeColumn('Last Seen'),
                'Status': st.column_config.SelectboxColumn('Status', options=['Active', 'Inactive', 'Blocked'])
            }
        )
        
        # Update session state if edited
        if not edited_df.equals(device_df):
            st.session_state['whitelisted_devices'] = edited_df
            st.success("Device list updated!")
        
        # Remove device section
        st.divider()
        st.subheader("Remove Device")
        device_to_remove = st.selectbox("Select Device to Remove", 
                                        options=['Select...'] + list(device_df['DeviceID'].values))
        if st.button("Remove Device"):
            if device_to_remove != 'Select...':
                st.session_state['whitelisted_devices'] = device_df[device_df['DeviceID'] != device_to_remove]
                st.success(f"Device {device_to_remove} removed from whitelist!")
                st.rerun()
    
    with tab2:
        st.subheader("Risk Thresholds")
        st.markdown("Configure fraud detection thresholds and rules.")
        
        thresholds = st.session_state['risk_thresholds']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Verdict Thresholds")
            new_allow = st.slider("ALLOW Threshold", 0.0, 1.0, thresholds['allow_threshold'], 0.05,
                                  help="Transactions below this score are automatically allowed")
            new_flag = st.slider("FLAG Threshold", 0.0, 1.0, thresholds['flag_threshold'], 0.05,
                                help="Transactions at or above this score are flagged for review")
            new_block = st.slider("BLOCK Threshold", 0.0, 1.0, thresholds['block_threshold'], 0.05,
                                 help="Transactions at or above this score are blocked")
            
            # Ensure logical ordering
            if new_allow >= new_flag:
                new_flag = new_allow + 0.05
                st.warning(f"FLAG threshold adjusted to {new_flag:.2f} to maintain logical ordering")
            if new_flag >= new_block:
                new_block = new_flag + 0.05
                st.warning(f"BLOCK threshold adjusted to {new_block:.2f} to maintain logical ordering")
            
            st.session_state['risk_thresholds']['allow_threshold'] = new_allow
            st.session_state['risk_thresholds']['flag_threshold'] = new_flag
            st.session_state['risk_thresholds']['block_threshold'] = new_block
            
            # Display current configuration
            st.info(f"""
            **Current Thresholds:**
            - ALLOW: < {new_allow:.2f}
            - FLAG: {new_allow:.2f} - {new_block:.2f}
            - BLOCK: ≥ {new_block:.2f}
            """)
        
        with col2:
            st.markdown("### Amount Thresholds (₹)")
            new_amount_high = st.number_input("High Amount Threshold", min_value=0, value=thresholds['amount_high'], step=1000)
            new_amount_critical = st.number_input("Critical Amount Threshold", min_value=0, value=thresholds['amount_critical'], step=5000)
            
            if new_amount_high >= new_amount_critical:
                new_amount_critical = new_amount_high + 10000
                st.warning(f"Critical threshold adjusted to ₹{new_amount_critical:,}")
            
            st.session_state['risk_thresholds']['amount_high'] = new_amount_high
            st.session_state['risk_thresholds']['amount_critical'] = new_amount_critical
            
            st.divider()
            
            st.markdown("### Unusual Hours Configuration")
            new_hour_start = st.slider("Unusual Hour Start", 0, 23, thresholds['unusual_hour_start'])
            new_hour_end = st.slider("Unusual Hour End", 0, 23, thresholds['unusual_hour_end'])
            
            if new_hour_start >= new_hour_end:
                st.warning("Start hour should be less than end hour for unusual hours configuration")
            
            st.session_state['risk_thresholds']['unusual_hour_start'] = new_hour_start
            st.session_state['risk_thresholds']['unusual_hour_end'] = new_hour_end
            
            st.info(f"**Unusual Hours:** {new_hour_start}:00 - {new_hour_end}:00")
        
        st.divider()
        
        # Save/Reset buttons
        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("Save Configuration"):
                st.success("Risk configuration saved for this session!")
        with col_reset:
            if st.button("Reset to Defaults"):
                st.session_state['risk_thresholds'] = {
                    'allow_threshold': 0.3,
                    'flag_threshold': 0.5,
                    'block_threshold': 0.8,
                    'amount_high': 10000,
                    'amount_critical': 50000,
                    'unusual_hour_start': 0,
                    'unusual_hour_end': 5
                }
                st.success("Configuration reset to defaults!")
                st.rerun()
    
    with tab3:
        st.subheader("Transaction Audit Logs")
        st.markdown("Review and export flagged/blocked transactions.")
        
        audit_df = st.session_state['audit_logs']
        
        # Search and filter section
        col_search1, col_search2 = st.columns([2, 1])
        
        with col_search1:
            search_term = st.text_input("Search by Transaction ID or UPI ID", placeholder="Enter search term...")
        
        with col_search2:
            verdict_filter = st.multiselect("Filter by Verdict", 
                                            options=['BLOCK', 'FLAG'],
                                            default=['BLOCK', 'FLAG'])
        
        # Apply filters
        filtered_df = audit_df.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['TransactionID'].str.contains(search_term, case=False, na=False) |
                filtered_df['SenderUPI'].str.contains(search_term, case=False, na=False)
            ]
        
        if verdict_filter:
            filtered_df = filtered_df[filtered_df['Verdict'].isin(verdict_filter)]
        
        # Display filtered results
        st.markdown(f"**Showing {len(filtered_df)} of {len(audit_df)} transactions**")
        
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df['Amount'] = display_df['Amount'].apply(lambda x: f"₹{x:,.2f}")
        display_df['RiskScore'] = display_df['RiskScore'].apply(lambda x: f"{x:.4f}")
        
        st.dataframe(display_df, use_container_width=True)
        
        # CSV Export
        st.divider()
        
        # Prepare CSV download
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        
        col_export, col_spacer = st.columns([1, 3])
        with col_export:
            st.download_button(
                label="📥 Export Filtered Logs to CSV",
                data=csv,
                file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download the filtered audit logs as a CSV file"
            )
        
        # Quick stats
        st.divider()
        st.markdown("### Quick Statistics")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        if len(filtered_df) > 0:
            col_stat1.metric("Total Flagged/Blocked", len(filtered_df))
            col_stat2.metric("BLOCKED", len(filtered_df[filtered_df['Verdict'] == 'BLOCK']))
            col_stat3.metric("FLAGGED", len(filtered_df[filtered_df['Verdict'] == 'FLAG']))
        else:
            st.info("No transactions match the current filters.")
