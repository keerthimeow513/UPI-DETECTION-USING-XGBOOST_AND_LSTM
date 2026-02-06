"""
Synthetic UPI transaction data generator for fraud detection model training.

This module generates realistic synthetic transaction data with various fraud patterns
including account takeover, SIM swap, and unusual location-based fraud.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import yaml
import sys

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.logger import setup_logger

logger = setup_logger()

# Initialize Faker with Indian locale for UPI context
fake = Faker('en_IN')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def load_config(config_path="07_configs/config.yaml"):
    """Load configuration from YAML file."""
    config_path = os.path.join(project_root, config_path)
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_upi_id(name):
    """Generate a UPI ID from a name."""
    return f"{name.lower().replace(' ', '')}{random.randint(1, 999)}@upi"

def generate_users(config):
    """Generate synthetic user profiles."""
    logger.info("Generating users...")
    num_users = config['data']['num_users']
    
    users = []
    for _ in range(num_users):
        user_id = fake.uuid4()
        name = fake.name()
        upi_id = generate_upi_id(name)
        primary_device = fake.mac_address()
        primary_location = (float(fake.latitude()), float(fake.longitude()))
        users.append({
            'user_id': user_id,
            'name': name,
            'upi_id': upi_id,
            'primary_device': primary_device,
            'primary_location': primary_location
        })
    
    return users

def generate_transactions(users, config):
    """Generate synthetic transaction data with fraud patterns."""
    logger.info("Generating transactions...")
    num_transactions = config['data']['num_transactions']
    fraud_rate = config['data']['fraud_rate']
    
    transactions = []
    start_date = datetime(2025, 1, 1)
    
    for _ in range(num_transactions):
        sender = random.choice(users)
        receiver = random.choice(users)
        while receiver['user_id'] == sender['user_id']:
            receiver = random.choice(users)
        
        # Base transaction details
        timestamp = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        amount = round(random.uniform(10, 5000), 2)
        device_id = sender['primary_device']
        location = sender['primary_location']
        is_fraud = 0
        
        # Introduce fraud patterns
        if random.random() < fraud_rate:
            is_fraud = 1
            fraud_type = random.choice(['account_takeover', 'sim_swap', 'unusual_location'])
            
            if fraud_type == 'account_takeover':
                # High amount, different device
                amount = round(random.uniform(10000, 100000), 2)
                device_id = fake.mac_address()
                
            elif fraud_type == 'sim_swap':
                # Transactions after long inactivity or high frequency
                amount = round(random.uniform(5000, 50000), 2)
                
            elif fraud_type == 'unusual_location':
                # Far location
                location = (float(fake.latitude()), float(fake.longitude()))
        
        transactions.append({
            'TransactionID': fake.uuid4(),
            'Timestamp': timestamp,
            'SenderName': sender['name'],
            'SenderUPI': sender['upi_id'],
            'ReceiverName': receiver['name'],
            'ReceiverUPI': receiver['upi_id'],
            'Amount': amount,
            'DeviceID': device_id,
            'Latitude': location[0],
            'Longitude': location[1],
            'IsFraud': is_fraud
        })
    
    return transactions

def save_data(transactions, config):
    """Save transaction data to CSV."""
    df = pd.DataFrame(transactions)
    df = df.sort_values(by='Timestamp')
    
    output_path = os.path.join(project_root, config['paths']['raw_data'])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    logger.info(f"Dataset generated at {output_path} with {len(df)} transactions.")
    return df

def main():
    """Main function to generate synthetic transaction data."""
    config = load_config()
    
    users = generate_users(config)
    transactions = generate_transactions(users, config)
    df = save_data(transactions, config)
    
    # Print summary statistics
    fraud_count = df['IsFraud'].sum()
    fraud_rate = fraud_count / len(df) * 100
    logger.info(f"Generated {len(df)} transactions with {fraud_count} fraud cases ({fraud_rate:.2f}%)")
    
    return df

if __name__ == "__main__":
    main()
