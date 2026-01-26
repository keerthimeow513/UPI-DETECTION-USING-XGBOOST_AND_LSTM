import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize Faker
fake = Faker('en_IN')  # Use Indian locale for UPI context
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_USERS = 1000
NUM_TRANSACTIONS = 20000
FRAUD_RATE = 0.02  # 2% fraud rate

def generate_upi_id(name):
    return f"{name.lower().replace(' ', '')}{random.randint(1, 999)}@upi"

print("Generating users...")
users = []
for _ in range(NUM_USERS):
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

print("Generating transactions...")
transactions = []
start_date = datetime(2025, 1, 1)

for _ in range(NUM_TRANSACTIONS):
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
    
    # Introduce Fraud Patterns
    if random.random() < FRAUD_RATE:
        is_fraud = 1
        fraud_type = random.choice(['account_takeover', 'sim_swap', 'unusual_location'])
        
        if fraud_type == 'account_takeover':
            # High amount, quick succession (simulated by just high amount here for simplicity in one row)
            amount = round(random.uniform(10000, 100000), 2)
            device_id = fake.mac_address() # Different device
            
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

# Convert to DataFrame
df = pd.DataFrame(transactions)

# Sort by timestamp for LSTM sequential nature
df = df.sort_values(by='Timestamp')

# Save
output_path = os.path.join('data', 'upi_transactions.csv')
df.to_csv(output_path, index=False)
print(f"Dataset generated at {output_path} with {len(df)} transactions.")
