import pandas as pd # Import pandas for data manipulation and analysis in tabular form (DataFrames)
import numpy as np # Import numpy for high-performance numerical operations on arrays
from sklearn.preprocessing import MinMaxScaler, LabelEncoder # Import tools to normalize numbers and convert text labels to numbers
import joblib # Import joblib to save and load serialized Python objects (like trained scalers)
import yaml # Import yaml to read configuration files in a human-readable format
import os # Import os for directory path handling and creation
from .logger import setup_logger # Import our custom logging utility from the local package

logger = setup_logger() # Initialize the logger for this specific module

class Preprocessor: # Define the main class responsible for all data cleaning and transformation
    def __init__(self, config_path="07_configs/config.yaml"): # Constructor to initialize the preprocessor with a config file
        with open(config_path, 'r') as f: # Open the YAML configuration file in read mode
            self.config = yaml.safe_load(f) # Parse the YAML content into a Python dictionary
        
        self.scalers = {} # Initialize an empty dictionary to store numerical scalers
        self.encoders = {} # Initialize an empty dictionary to store categorical encoders
        self.feature_names = [] # Initialize an empty list to keep track of final feature order
        
    def feature_engineering(self, df): # Method to create new predictive signals from raw transaction data
        logger.info("Starting feature engineering...") # Log the start of the feature creation process
        df['Timestamp'] = pd.to_datetime(df['Timestamp']) # Convert the 'Timestamp' string column into actual datetime objects
        
        # Temporal Features
        df['Hour'] = df['Timestamp'].dt.hour # Extract the hour of the day (0-23) as a new feature
        df['DayOfWeek'] = df['Timestamp'].dt.dayofweek # Extract the day of the week (0=Mon, 6=Sun) as a new feature
        df['DayOfMonth'] = df['Timestamp'].dt.day # Extract the specific day of the month as a new feature
        
        # Sorting
        df = df.sort_values(by=['SenderUPI', 'Timestamp']) # Sort data by user and time to ensure sequential analysis is correct
        
        # Lag Features
        df['TimeDiff'] = df.groupby('SenderUPI')['Timestamp'].diff().dt.total_seconds().fillna(0) # Calculate seconds passed since user's last transaction
        df['AmountDiff'] = df.groupby('SenderUPI')['Amount'].diff().fillna(0) # Calculate the change in amount compared to the user's last transaction
        
        return df # Return the enriched DataFrame with new features
        
    def fit_transform(self, df): # Method to learn data distributions and transform the dataset for training
        logger.info("Fitting and transforming data...") # Log the start of the scaling and encoding process
        df = self.feature_engineering(df) # First, run feature engineering to add temporal/lag columns
        
        # Categorical
        for col in self.config['features']['categorical']: # Loop through each categorical column defined in the config
            le = LabelEncoder() # Initialize a new label encoder for this specific column
            df[col] = le.fit_transform(df[col].astype(str)) # Convert text to numbers and store the mapping logic
            self.encoders[col] = le # Save the encoder instance to reuse during live inference
            
        # Numerical
        num_cols = self.config['features']['numerical'] # Retrieve the list of numerical columns from config
        scaler = MinMaxScaler() # Initialize a scaler to shrink values between 0 and 1 (crucial for LSTMs)
        df[num_cols] = scaler.fit_transform(df[num_cols]) # Calculate min/max and scale the numerical data
        self.scalers['scaler'] = scaler # Save the scaler instance to reuse during live inference
        
        self.feature_names = num_cols + self.config['features']['categorical'] # Define the final ordered list of feature names
        
        # Save artifacts
        self.save_artifacts() # Export the encoders/scalers to disk so the API can load them later
        return df # Return the fully processed and numerical DataFrame
        
    def transform_single(self, data_dict): # Method to transform a single live transaction for real-time prediction
        """Transform a single dictionary input for inference"""
        # Load artifacts if not in memory
        if not self.encoders: # If encoders haven't been loaded into memory yet...
            self.load_artifacts() # ...load them from the saved .pkl files
            
        # 1. Encode Categorical
        cat_features = [] # Initialize list for processed categorical values
        for col in self.config['features']['categorical']: # Loop through each required categorical field
            val = str(data_dict.get(col, '')) # Safely get the value from input dictionary or empty string
            try: # Use a try block to handle cases where a user might have a new, unseen ID
                # Handle unseen labels carefully
                encoded_val = self.encoders[col].transform([val])[0] # Transform the single value using the fitted encoder
            except: # If the label was never seen during training...
                encoded_val = 0 # ...default to 0 to prevent the system from crashing
            cat_features.append(encoded_val) # Add the numerical version of the category to our list
            
        # 2. Scale Numerical
        # Note: In real-time, diff features (TimeDiff, AmountDiff) need history.
        # For this demo, we assume they are provided or default to 0.
        num_vals = [data_dict.get(col, 0) for col in self.config['features']['numerical']] # Gather numerical inputs in correct order
        num_scaled = self.scalers['scaler'].transform([num_vals])[0] # Scale the numerical inputs using the saved scaler
        
        return np.concatenate([num_scaled, cat_features]) # Merge numerical and categorical lists into a single flat array

    def create_sequences(self, df, lookback=None): # Method to restructure data into 3D shapes for LSTM (Sequences of transactions)
        if lookback is None: # If no custom lookback is provided...
            lookback = self.config['data']['lookback'] # ...use the value from the config file (e.g., last 10 txns)
            
        logger.info(f"Creating sequences with lookback {lookback}...") # Log the sequence creation parameters
        
        X_lstm = [] # List to hold the 3D sequence data for LSTM
        X_xgb = [] # List to hold the 1D current transaction data for XGBoost
        y = [] # List to hold the target labels (Fraud or Not)
        
        feature_cols = self.feature_names # Use the previously determined feature list
        
        grouped = df.groupby('SenderUPI') # Group transactions by user to ensure sequences don't mix different people
        
        for _, group in grouped: # Iterate through each user's transaction history
            data = group[feature_cols].values # Convert the user's features into a raw numpy matrix
            target = group['IsFraud'].values # Get the corresponding fraud labels for that user
            
            if len(data) < lookback: # If the user has fewer transactions than our lookback window...
                continue # ...skip them as we can't form a full sequence
                
            for i in range(lookback, len(data)): # Slide a window across the user's history
                X_lstm.append(data[i-lookback:i]) # Store the previous 'n' transactions as the sequence input
                X_xgb.append(data[i]) # Store the current (most recent) transaction as the flat input
                y.append(target[i]) # Store the fraud label of the current transaction
                
        return np.array(X_lstm), np.array(X_xgb), np.array(y) # Return processed data as optimized numpy arrays

    def save_artifacts(self): # Method to export processing logic to files
        os.makedirs(self.config['paths']['artifacts'], exist_ok=True) # Ensure the artifacts directory exists
        joblib.dump(self.encoders, os.path.join(self.config['paths']['artifacts'], 'label_encoders.pkl')) # Save categorical mappings
        joblib.dump(self.scalers['scaler'], os.path.join(self.config['paths']['artifacts'], 'scaler.pkl')) # Save numerical min/max values
        joblib.dump(self.feature_names, os.path.join(self.config['paths']['artifacts'], 'feature_names.pkl')) # Save the exact feature order
        logger.info("Artifacts saved.") # Log completion of export

    def load_artifacts(self): # Method to import processing logic from files
        path = self.config['paths']['artifacts'] # Get the directory where artifacts are stored
        self.encoders = joblib.load(os.path.join(path, 'label_encoders.pkl')) # Reload the categorical mappings
        self.scalers['scaler'] = joblib.load(os.path.join(path, 'scaler.pkl')) # Reload the numerical scaler
        self.feature_names = joblib.load(os.path.join(path, 'feature_names.pkl')) # Reload the feature list
