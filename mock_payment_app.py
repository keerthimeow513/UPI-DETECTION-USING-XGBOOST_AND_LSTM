import requests # Import the requests library to make HTTP calls to our Fraud Detection API
import json # Import json to handle data formatting
import time # Import time to simulate network delays and measure latency
import os # Import os to access environment variables
from urllib.parse import urljoin

# Configuration: Load API URL from environment variable or use default
API_BASE_URL = os.getenv('API_URL', 'http://localhost:8000')
API_URL = urljoin(API_BASE_URL.rstrip('/') + '/', 'predict')

def main(): # The main entry point for our simulation app
    print("="*50) # UI separator
    print("      MOCK UPI PAYMENT APP (DEMO)      ") # App title
    print("="*50) # UI separator
    print("Simulating integration with AI Fraud Detection System...\n") # Context message
    print(f"Connected to: {API_BASE_URL}\n") # Show which API server we're using

    # Simulate a logged-in user (hardcoded for demonstration purposes)
    user_upi = "neelimabutala513@upi" # A sample user from our training dataset
    print(f"Logged in as: {user_upi}") # Show current user
    print(f"Device ID: 82:4e:8e:2a:9e:28") # Show the user's registered device MAC address
    print("-" * 50) # UI separator

    while True: # Start an infinite loop to allow multiple payment tests
        print("\nMake a Payment:") # Menu header
        print("1. Normal Payment (You)") # Option for safe behavior
        print("2. Simulate Hacker Attack (Stolen Credentials)") # Option for malicious behavior
        print("q. Quit") # Option to exit
        choice = input("Select Option: ") # Capture user input

        if choice.lower() == 'q': # If user wants to quit...
            break # ...exit the loop
        
        # Determine simulation parameters based on user choice
        device_id = "82:4e:8e:2a:9e:28" # Default to the registered "Safe" device
        lat = -35.45 # Default to the user's home latitude
        long = -96.58 # Default to the user's home longitude
        is_attack = False # Boolean flag to track if we are in attack mode

        if choice == '2': # If the user chose to simulate an attack
            is_attack = True # Set the attack flag to true
            print("\n[WARNING] SIMULATING ATTACK: Unrecognized Device & Unusual Location...") # Alert the user
            device_id = "11:22:33:44:55:66" # Use an unknown device ID that the AI hasn't seen for this user
            lat = 12.97 # Change location to somewhere far away (Bangalore, India)
            long = 77.59
        elif choice != '1': # Handle invalid menu selections
            print("Invalid option.") # Print error message
            continue # Restart the loop

        receiver = input("Enter Receiver UPI: ") # Ask for the destination UPI ID
        try: # Use a try-except to handle non-numeric amount inputs
            amount = float(input("Enter Amount (₹): ")) # Capture and convert the payment amount
        except ValueError: # If the input isn't a valid number...
            print("Invalid amount!") # ...print an error
            continue # ...restart the loop

        print("\n[PROCESS] Processing Payment...") # Status message
        time.sleep(1) # Simulate the real-world delay of a banking transaction
        
        # 1. Construct the JSON payload to send to the AI API
        payload = {
            "SenderUPI": user_upi, # The sender's ID
            "ReceiverUPI": receiver, # The receiver's ID
            "Amount": amount, # The money value
            "DeviceID": device_id, # The hardware ID (Crucial for fraud detection)
            "Latitude": lat, # GPS Lat
            "Longitude": long, # GPS Long
            "Timestamp": None # Let the server decide the time
        }
        
        # 2. Call the AI API (The actual integration point)
        try:
            print("[SIGNAL] Contacting Bank Fraud Detection Server...") # Status message
            start_time = time.time() # Start a timer to measure API speed
            response = requests.post(API_URL, json=payload) # Send the data via a POST request
            latency = (time.time() - start_time) * 1000 # Calculate response time in milliseconds
            
            if response.status_code == 200: # If the API call was successful (HTTP 200)
                result = response.json() # Parse the JSON result from the server
                
                print(f"Server Response: {latency:.0f}ms") # Show the API speed
                print("-" * 50) # UI separator
                
                # 3. Handle the Fraud Verdict returned by the AI
                if result['verdict'] == "BLOCK": # If the AI says the risk is too high
                    print("\n[BLOCK] [ALERT] TRANSACTION BLOCKED!") # Big red block message
                    print("Reason: High Fraud Risk Detected") # Explain why
                    print(f"Risk Score: {result['risk_score']:.4f}") # Show the probability
                    print("\nSuspicious Factors:") # List the reasons
                    for factor, impact in result['factors'].items(): # Iterate through the SHAP values
                        print(f" - {factor}: {impact:.4f}") # Show how much each factor added to the risk
                        
                elif result['verdict'] == "FLAG": # If the AI is suspicious but not certain
                    print("\n[WARNING] TRANSACTION FLAGGED FOR REVIEW") # Warning message
                    print("Please verify this transaction via OTP.") # Actionable step
                    print(f"Risk Score: {result['risk_score']:.4f}") # Show the score
                    
                else: # If the AI says the transaction is safe
                    if is_attack: # If we were simulating an attack but it got through...
                        print("\n[NOTE]: System allowed this. Model might need retraining or attack pattern too subtle.")
                    print("\n[SUCCESS] PAYMENT SUCCESSFUL") # Success message
                    print(f"Paid ₹{amount} to {receiver}") # Final transaction summary
                    print(f"Risk Score: {result['risk_score']:.4f} (Safe)") # Show the safe score
                    
            else: # If the server returned an error code (like 500)
                print(f"Error: Server returned {response.status_code}") # Show the code
                print(response.text) # Show the error message
                
        except requests.exceptions.ConnectionError: # If the API server isn't running
            print("\n[BLOCK] Error: Could not connect to Fraud Detection Server.") # Error message
            print("Make sure 'uvicorn 04_inference.api:app' is running!") # Helpful instruction

if __name__ == "__main__": # Standard Python entry point check
    main() # Run the app
