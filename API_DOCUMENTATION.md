# API Documentation

Complete API reference for the UPI Fraud Detection System.

## Base URLs

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8000` |
| Production | `https://api.yourdomain.com` |

## Versioning

Current API Version: `v1`

API versioning is implemented via URL path: `/v1/`

## Authentication

Currently, the API does not require authentication for development purposes. For production deployment, JWT authentication should be enabled.

### Enabling JWT Authentication

1. Set environment variables:
   ```env
   JWT_SECRET=your-secure-secret-key
   JWT_ALGORITHM=HS256
   ```

2. Include authorization header:
   ```http
   Authorization: Bearer <token>
   ```

## Rate Limiting

The API implements rate limiting using SlowAPI.

| Endpoint | Limit |
|----------|-------|
| `/` (Health Check) | 100 requests/minute |
| `/predict` | 10 requests/minute |

### Rate Limit Headers

All responses include rate limit headers:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
    "error": "Rate limit exceeded",
    "message": "Too many requests",
    "retry_after": 60
}
```

## Endpoints

### Health Check

**Endpoint:** `GET /`

**Description:** Returns the system status and health information.

**Rate Limit:** 100 requests/minute

**Response:**

```json
{
    "status": "online",
    "system": "UPI Fraud Shield",
    "environment": "development",
    "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - System is healthy

---

### Predict Fraud

**Endpoint:** `POST /predict`

**Description:** Analyzes a transaction and returns fraud risk assessment.

**Rate Limit:** 10 requests/minute

**Content-Type:** `application/json`

#### Request Body

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| SenderUPI | string | Yes | 3-100 chars, format `user@upi` | Sender's UPI ID |
| ReceiverUPI | string | Yes | 3-100 chars, format `user@upi` | Receiver's UPI ID |
| Amount | number | Yes | 0 < amount ≤ 10,000,000 | Transaction amount in INR |
| DeviceID | string | Yes | 1-100 chars | Device identifier (MAC/IMEI) |
| Latitude | number | Yes | -90 ≤ lat ≤ 90 | GPS latitude |
| Longitude | number | Yes | -180 ≤ long ≤ 180 | GPS longitude |
| Timestamp | string | No | ISO 8601 format | Transaction timestamp |
| Hour | integer | No | 0-23 | Hour of transaction |
| DayOfWeek | integer | No | 0-6 | Day of week (0=Monday) |
| DayOfMonth | integer | No | 1-31 | Day of month |
| TimeDiff | integer | No | ≥ 0 | Time since last transaction (seconds) |
| AmountDiff | number | No | ≥ 0 | Amount difference from average |

#### Example Request

```json
{
    "SenderUPI": "user@upi",
    "ReceiverUPI": "merchant@upi",
    "Amount": 5000.0,
    "DeviceID": "82:4e:8e:2a:9e:28",
    "Latitude": 12.97,
    "Longitude": 77.59,
    "Hour": 14,
    "DayOfWeek": 1,
    "DayOfMonth": 15,
    "TimeDiff": 3600,
    "AmountDiff": 1000
}
```

#### Response Body

| Field | Type | Description |
|-------|------|-------------|
| transaction_id | string | UUID of the transaction |
| risk_score | number | Fraud probability (0.0 - 1.0) |
| verdict | string | Decision: ALLOW, FLAG, or BLOCK |
| lstm_score | number | LSTM model probability |
| xgb_score | number | XGBoost model probability |
| factors | object | Top contributing risk factors |

#### Verdict Values

| Verdict | Risk Score Range | Action |
|---------|-----------------|--------|
| ALLOW | 0.0 - 0.5 | Transaction approved |
| FLAG | 0.5 - 0.8 | Additional verification needed |
| BLOCK | 0.8 - 1.0 | Transaction rejected |

#### Example Response

```json
{
    "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
    "risk_score": 0.75,
    "verdict": "BLOCK",
    "lstm_score": 0.72,
    "xgb_score": 0.78,
    "factors": {
        "Unknown Device": 0.35,
        "High Amount": 0.25,
        "Unusual Hour": 0.15,
        "Velocity": 0.10,
        "Geolocation": 0.05
    }
}
```

#### Status Codes

| Code | Description |
|------|-------------|
| 200 OK | Successful prediction |
| 400 Bad Request | Invalid request parameters |
| 422 Unprocessable Entity | Validation error |
| 429 Too Many Requests | Rate limit exceeded |
| 500 Internal Server Error | Server error |

---

## Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 40001 | INVALID_UPI_FORMAT | UPI ID format is invalid |
| 40002 | INVALID_AMOUNT | Amount is outside allowed range |
| 40003 | INVALID_DEVICE_ID | Device ID is missing or invalid |
| 40004 | INVALID_GEOLOCATION | Latitude/longitude out of range |
| 42201 | VALIDATION_ERROR | Request validation failed |
| 42901 | RATE_LIMIT_EXCEEDED | Too many requests |
| 50001 | MODEL_LOADING_ERROR | Failed to load ML models |
| 50002 | PREDICTION_ERROR | Failed to process prediction |
| 50003 | SERVICE_UNAVAILABLE | Service is not ready |

### Error Response Format

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {
            "field": "Additional error details"
        }
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## CORS Configuration

The API supports Cross-Origin Resource Sharing (CORS).

### Allowed Origins (Development)

```json
[
    "http://localhost:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8000"
]
```

### CORS Headers

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
```

## API Clients

### Python (httpx)

```python
import httpx

async def predict_fraud(transaction: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/predict",
            json=transaction
        )
        return response.json()
```

### JavaScript (fetch)

```javascript
async function predictFraud(transaction) {
    const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(transaction)
    });
    return response.json();
}
```

### cURL

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "SenderUPI": "user@upi",
    "ReceiverUPI": "merchant@upi",
    "Amount": 5000.0,
    "DeviceID": "82:4e:8e:2a:9e:28",
    "Latitude": 12.97,
    "Longitude": 77.59,
    "Hour": 14,
    "DayOfWeek": 1
  }'
```

## WebSocket Support

Real-time fraud detection via WebSocket is planned for future release.

## Deprecation Policy

- APIs are deprecated with 90-day notice
- Deprecated APIs return `Deprecation` header
- Migration guides provided for major version changes

## Support

For API issues, contact: api-support@yourdomain.com

## Changelog

### v1.0.0 (2024-01-15)

- Initial API release
- Health check endpoint
- Fraud prediction endpoint
- Rate limiting implemented
- CORS support added
