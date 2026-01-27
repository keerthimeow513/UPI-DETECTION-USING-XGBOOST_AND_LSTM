# Simple Upgrade Guide for UPI Fraud Detection

This guide provides three "Low-Complexity" upgrades to move this project closer to a production-ready system.

---

## Upgrade 1: Real-Time History (The "Memory" Upgrade)
**Current State:** The LSTM model uses a "mocked" history (it repeats the current transaction 10 times).
**The Goal:** Use the user's *actual* last 10 transactions to detect behavioral changes.

### Implementation Steps:
1.  **Add a simple history store:** In a real app, you would use a database. For a simple upgrade, use a JSON file or a Python dictionary that persists.
2.  **Update `service.py`:**
    ```python
    # New logic to fetch real history
    user_history = {} # In-memory storage (Dictionary)

    def predict(self, transaction_data):
        user_id = transaction_data['SenderUPI']
        
        # 1. Get current features
        current_features = self.preprocessor.transform_single(transaction_data)
        
        # 2. Update history
        if user_id not in user_history:
            user_history[user_id] = []
        
        user_history[user_id].append(current_features)
        
        # Keep only the last 10
        if len(user_history[user_id]) > 10:
            user_history[user_id].pop(0)
            
        # 3. Use real sequence if available, otherwise pad
        if len(user_history[user_id]) == 10:
            lstm_input = np.array(user_history[user_id]).reshape(1, 10, -1)
        else:
            # Pad with current features if history is short
            lstm_input = np.tile(current_features, (1, 10, 1))
    ```

---

## Upgrade 2: Geofencing (The "Physical Reality" Upgrade)
**Current State:** The AI checks GPS, but it doesn't know how fast a person can travel.
**The Goal:** Block transactions that happen in two distant cities too quickly ("Impossible Travel").

### Implementation Example:
Add this simple logic to your `service.py` under the "Domain Rules" section:

```python
from geopy.distance import geodesic # Install via 'pip install geopy'

def check_velocity(last_txn, current_txn):
    # Calculate distance in km
    dist = geodesic((last_txn['Lat'], last_txn['Long']), 
                    (current_txn['Lat'], current_txn['Long'])).km
    
    # Calculate time difference in hours
    time_diff = (current_txn['Time'] - last_txn['Time']).total_seconds() / 3600
    
    # If speed > 800 km/h (speed of a plane), it's suspicious!
    if time_diff > 0 and (dist / time_diff) > 800:
        return True # Trigger Fraud Alert
    return False
```

---

## Upgrade 3: Instant Deployment with Docker
**Current State:** You have to manually install libraries and run `uvicorn`.
**The Goal:** Run the API on any computer (Windows, Mac, Linux) without installing Python.

### Create a file named `Dockerfile` in the root folder:
```dockerfile
# 1. Use a lightweight Python image
FROM python:3.9-slim

# 2. Set the working directory
WORKDIR /app

# 3. Copy only the requirements first (to cache layers)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the project
COPY . .

# 6. Expose the API port
EXPOSE 8000

# 7. Command to run the API
CMD ["uvicorn", "04_inference.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**To Run:**
1. `docker build -t upi-fraud-api .`
2. `docker run -p 8000:8000 upi-fraud-api`

---

## Summary of Benefits
| Upgrade | Complexity | Benefit |
| :--- | :--- | :--- |
| **Real History** | Low | Makes the LSTM model actually "see" patterns over time. |
| **Geofencing** | Medium | Catches sophisticated hackers using stolen credentials from far away. |
| **Docker** | Low | Ensures the system works the same on every developer's machine. |
