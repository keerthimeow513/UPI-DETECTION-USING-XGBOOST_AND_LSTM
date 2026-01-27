import sys
import os

# Add project root and inference folder to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, '04_inference'))

# Disable GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from service import FraudDetectionService

def test_scenarios():
    service = FraudDetectionService('07_configs/config.yaml')
    
    scenarios = [
        {
            "name": "Case 1: The Regular User",
            "data": {
                "SenderUPI": "user@upi",
                "ReceiverUPI": "shop@upi",
                "Amount": 1200.0,
                "DeviceID": "82:4e:8e:2a:9e:28",
                "Latitude": -35.45,
                "Longitude": -96.58,
                "Hour": 14,
                "DayOfWeek": 1
            },
            "expected": "ALLOW"
        },
        {
            "name": "Case 2: The New Phone User",
            "data": {
                "SenderUPI": "user@upi",
                "ReceiverUPI": "shop@upi",
                "Amount": 1200.0,
                "DeviceID": "new_device_id",
                "Latitude": -35.45,
                "Longitude": -96.58,
                "Hour": 14,
                "DayOfWeek": 1
            },
            "expected": "FLAG"
        },
        {
            "name": "Case 3: The Late Night Shopper (Safe Device)",
            "data": {
                "SenderUPI": "user@upi",
                "ReceiverUPI": "shop@upi",
                "Amount": 15000.0,
                "DeviceID": "82:4e:8e:2a:9e:28",
                "Latitude": -35.45,
                "Longitude": -96.58,
                "Hour": 3,
                "DayOfWeek": 1
            },
            "expected": "FLAG"
        },
        {
            "name": "Case 4: The Hacker",
            "data": {
                "SenderUPI": "user@upi",
                "ReceiverUPI": "hacker@upi",
                "Amount": 45000.0,
                "DeviceID": "hacker_device",
                "Latitude": 12.97,
                "Longitude": 77.59,
                "Hour": 3,
                "DayOfWeek": 1
            },
            "expected": "BLOCK"
        }
    ]

    print("\n" + "="*50)
    print("VERIFYING FRAUD DETECTION SCENARIOS")
    print("="*50 + "\n")

    for scene in scenarios:
        print(f"Running {scene['name']}...")
        result = service.predict(scene['data'])
        print(f"Result: {result['verdict']} (Score: {result['risk_score']:.4f})")
        
        if result['verdict'] == scene['expected']:
            print("Status: PASS\n")
        else:
            print(f"Status: FAIL (Expected {scene['expected']})\n")

if __name__ == "__main__":
    test_scenarios()
