import requests
import json
import time
import random

# Configuration (Point to your local API)
API_URL = "http://localhost:8000/predict"

def main():
    print("="*50)
    print("      📱 MOCK UPI PAYMENT APP (DEMO)      ")
    print("="*50)
    print("Simulating integration with AI Fraud Detection System...\n")

    # Simulate User Login
    user_upi = "neelimabutala513@upi" # From our dataset
    print(f"👤 Logged in as: {user_upi}")
    print(f"📱 Device ID: 82:4e:8e:2a:9e:28")
    print("-" * 50)

    while True:
        print("\nMake a Payment:")
        receiver = input("Enter Receiver UPI (or 'q' to quit): ")
        if receiver.lower() == 'q':
            break
            
        try:
            amount = float(input("Enter Amount (₹): "))
        except ValueError:
            print("Invalid amount!")
            continue

        print("\n🔄 Processing Payment...")
        time.sleep(1) # Simulate network delay
        
        # 1. Construct the Payload (Simulating what GPay sends to the server)
        # We auto-fill location/time for the demo
        payload = {
            "SenderUPI": user_upi,
            "ReceiverUPI": receiver,
            "Amount": amount,
            "DeviceID": "82:4e:8e:2a:9e:28", # Known device
            "Latitude": -35.45,  # User's home location
            "Longitude": -96.58,
            "Timestamp": None # API will handle time
        }
        
        # 2. Call the AI API (The Integration)
        try:
            print("📡 Contacting Bank Fraud Detection Server...")
            start_time = time.time()
            response = requests.post(API_URL, json=payload)
            latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"⏱️  Server Response: {latency:.0f}ms")
                print("-" * 50)
                
                # 3. Handle Verdict
                if result['verdict'] == "BLOCK":
                    print("\n❌ 🚨 TRANSACTION BLOCKED! 🚨")
                    print("Reason: High Fraud Risk Detected")
                    print(f"Risk Score: {result['risk_score']:.4f}")
                    print("\nSuspicious Factors:")
                    for factor, impact in result['factors'].items():
                        print(f" - {factor}: {impact:.4f}")
                        
                elif result['verdict'] == "FLAG":
                    print("\n⚠️  TRANSACTION FLAGGED FOR REVIEW")
                    print("Please verify this transaction via OTP.")
                    print(f"Risk Score: {result['risk_score']:.4f}")
                    
                else:
                    print("\n✅ PAYMENT SUCCESSFUL")
                    print(f"Paid ₹{amount} to {receiver}")
                    print(f"Risk Score: {result['risk_score']:.4f} (Safe)")
                    
            else:
                print(f"Error: Server returned {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to Fraud Detection Server.")
            print("Make sure 'uvicorn 04_inference.api:app' is running!")

if __name__ == "__main__":
    main()
