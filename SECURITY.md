# Security Documentation

Comprehensive security documentation for the UPI Fraud Detection System.

## Security Overview

The UPI Fraud Detection System implements multiple layers of security to protect against threats and ensure the integrity, confidentiality, and availability of the fraud detection service.

## Security Features Implemented

### 1. API Security

#### Rate Limiting

The API implements rate limiting to prevent abuse and DDoS attacks.

| Endpoint | Limit | Burst |
|----------|-------|-------|
| `/` (Health) | 100/minute | 200 |
| `/predict` | 10/minute | 20 |

**Implementation:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

#### Input Validation

All inputs are validated using Pydantic schemas with strict type checking and constraints.

```python
class TransactionRequest(BaseModel):
    SenderUPI: str = Field(..., min_length=3, max_length=100)
    ReceiverUPI: str = Field(..., min_length=3, max_length=100)
    Amount: float = Field(..., ge=0, le=10000000)
    DeviceID: str = Field(..., min_length=1, max_length=100)
    Latitude: float = Field(..., ge=-90, le=90)
    Longitude: float = Field(..., ge=-180, le=180)
    
    @field_validator('SenderUPI', 'ReceiverUPI')
    @classmethod
    def validate_upi(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('UPI ID must contain @ symbol')
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$', v):
            raise ValueError('UPI ID format invalid')
        return v
```

#### CORS Configuration

CORS is configured to allow only trusted origins.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Model Security

#### Secure Model Loading

Models are loaded with integrity verification to prevent tampering.

```python
from utils.security import (
    SecureModelLoader,
    calculate_checksum,
    validate_model_integrity,
    secure_load_pickle
)

class FraudDetectionService:
    def __init__(self, config_path):
        self.secure_loader = SecureModelLoader(
            models_dir=path,
            checksums_file=checksums_file,
            verify_checksums=True
        )
    
    def load_models(self):
        # Load with security validation
        self.xgb_model = self.secure_loader.load_model('xgb_model.pkl')
```

#### Checksum Validation

Model files are validated against checksums before loading.

**Generating Checksums:**
```python
import hashlib
import json

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Generate checksums.json
checksums = {
    "lstm_model.h5": calculate_checksum("02_models/artifacts/lstm_model.h5"),
    "xgb_model.pkl": calculate_checksum("02_models/artifacts/xgb_model.pkl"),
    "scaler.pkl": calculate_checksum("02_models/artifacts/scaler.pkl")
}
with open("02_models/artifacts/checksums.json", "w") as f:
    json.dump(checksums, f, indent=2)
```

#### Restricted Unpickling

Pickle files are loaded with restricted unpickler to prevent code execution attacks.

```python
import pickle
import io

class RestrictedUnpickler(pickle.Unpickler):
    """Restricted unpickler that only allows safe types."""
    
    def find_class(self, module, name):
        # Whitelist allowed classes
        allowed_modules = {
            'numpy': ['ndarray', 'dtype', 'array'],
            'sklearn': ['GradientBoostingClassifier', 'model'],
        }
        
        if module.split('.')[0] in allowed_modules:
            if name in allowed_modules[module.split('.')[0]]:
                return super().find_class(module, name)
        
        raise pickle.UnpicklingError(f"Forbidden class: {module}.{name}")

def secure_load_pickle(file_path):
    """Load pickle file with restricted unpickler."""
    with open(file_path, 'rb') as f:
        return RestrictedUnpickler(f).load()
```

### 3. Authentication & Authorization

#### JWT Authentication (Production)

JWT tokens are used for API authentication in production environments.

```python
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/predict")
async def predict_fraud(
    request: TransactionRequest,
    token: dict = Depends(verify_token)
):
    # Process authenticated request
    pass
```

#### Password Hashing

User passwords are hashed using bcrypt.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 4. Data Protection

#### Sensitive Data Handling

| Data Type | Protection Method | Storage |
|-----------|------------------|---------|
| API Keys | Environment variables | Secrets manager |
| Model Files | Checksum validation | Encrypted storage |
| User Data | Minimal retention | In-memory/Redis |
| Logs | Anonymization | Separate log store |

#### Data Anonymization

```python
def anonymize_transaction(transaction: dict) -> dict:
    """Remove PII from transaction data for logging."""
    return {
        "amount": transaction["Amount"],
        "timestamp": transaction.get("Timestamp"),
        "risk_score": transaction.get("risk_score"),
        # Remove PII
    }
```

### 5. Domain Rules Security

#### Security Configuration

```yaml
security:
  # Known safe devices (whitelist)
  known_safe_devices:
    - "82:4e:8e:2a:9e:28"
    - "device_id_2"
  
  # Risk thresholds
  risk_thresholds:
    block: 0.8
    flag: 0.5
  
  # Amount thresholds
  amount_thresholds:
    high: 10000
    critical: 50000
  
  # Unusual hours
  unusual_hours:
    start: 0
    end: 5
  
  # Velocity thresholds
  velocity_thresholds:
    transactions_per_hour: 5
    amount_per_hour: 50000
```

#### Rule Enforcement

```python
class SecurityRules:
    def __init__(self, config):
        self.known_safe_devices = config.get('known_safe_devices', [])
        self.velocity_thresholds = config.get('velocity_thresholds', {})
    
    def check_unknown_device(self, device_id: str) -> tuple[bool, float]:
        """Check if device is unknown and return risk score."""
        if device_id not in self.known_safe_devices:
            return True, 0.30  # Unknown device adds 30% risk
        return False, 0.0
    
    def check_velocity(self, user_id: str, feature_store) -> tuple[bool, float]:
        """Check for suspicious transaction velocity."""
        txns_last_hour = feature_store.get_transaction_count(user_id, hours=1)
        threshold = self.velocity_thresholds.get('transactions_per_hour', 5)
        
        if txns_last_hour > threshold:
            return True, 0.45  # High velocity adds 45% risk
        return False, 0.0
```

## Compliance Considerations

### Data Privacy

#### GDPR Compliance

| Requirement | Implementation |
|-------------|---------------|
| Data minimization | Only collect required fields |
| Purpose limitation | Data used only for fraud detection |
| Storage limitation | Automatic data purging |
| Right to access | API endpoint for data export |
| Right to deletion | API endpoint for data deletion |

#### Data Retention

```python
# Automatic data purging
from datetime import datetime, timedelta

class DataRetentionPolicy:
    RETENTION_DAYS = 90
    
    def cleanup_old_data(self):
        cutoff_date = datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
        # Delete data older than cutoff_date
```

### Audit Logging

#### Audit Log Structure

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "event_type": "PREDICTION_REQUEST",
    "user_id": "user@upi",
    "transaction_id": "uuid",
    "ip_address": "192.168.1.1",
    "request_id": "uuid",
    "risk_score": 0.75,
    "verdict": "BLOCK",
    "processing_time_ms": 45
}
```

#### Audit Endpoints

```python
@app.get("/audit/logs")
async def get_audit_logs(
    start_date: datetime,
    end_date: datetime,
    token: dict = Depends(verify_token)
):
    # Return audit logs for date range
    pass

@app.get("/audit/export")
async def export_audit_logs(
    start_date: datetime,
    end_date: datetime,
    token: dict = Depends(verify_token)
):
    # Export audit logs as CSV
    pass
```

## Security Best Practices

### Deployment Security

1. **Use HTTPS in production**
   ```bash
   # With uvicorn
   uvicorn main:app --ssl-certfile cert.pem --ssl-keyfile key.pem
   ```

2. **Secret management**
   ```bash
   # Use environment variables or secrets manager
   export JWT_SECRET=$(openssl rand -hex 32)
   export DATABASE_PASSWORD=$(aws secretsmanager get-secret-value)
   ```

3. **Container security**
   ```dockerfile
   # Dockerfile security best practices
   FROM python:3.11-slim
   
   # Create non-root user
   RUN groupadd -r appgroup && useradd -r -g appgroup appuser
   USER appuser
   
   # No root access
   ```

4. **Network security**
   ```yaml
   # docker-compose network isolation
   services:
     api:
       networks:
         - internal_network
     
     redis:
       networks:
         - internal_network
       internal: true
   ```

### Monitoring and Incident Response

#### Security Monitoring

```python
# Suspicious activity detection
class SecurityMonitor:
    def detect_brute_force(self, ip_address: str) -> bool:
        failed_attempts = cache.get(f"failed:{ip_address}", 0)
        if failed_attempts > 5:
            return True
        return False
    
    def log_security_event(self, event_type: str, details: dict):
        logger.warning(f"Security event: {event_type}", extra=details)
```

#### Incident Response Plan

| Phase | Actions |
|-------|---------|
| Detection | Automated alerts, monitoring dashboards |
| Analysis | Log review, correlation analysis |
| Containment | Block IPs, disable accounts |
| Eradication | Patch vulnerabilities, remove threats |
| Recovery | Restore services, verify integrity |
| Lessons Learned | Update security measures |

## Vulnerability Management

### Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scanning

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r 04_inference/
      
      - name: Run Safety
        run: |
          pip install safety
          safety check -r requirements.txt
      
      - name: Dependency Review
        uses: actions/dependency-review-action@v1
```

### Known Vulnerabilities

| Dependency | Version | CVE | Status |
|------------|---------|-----|--------|
| scikit-learn | < 1.6.1 | CVE-2024-5206 | Fixed |
| tensorflow | < 2.18.0 | Various | Monitor |

## Security Checklist

### Pre-Deployment

- [ ] Enable HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up authentication
- [ ] Enable audit logging
- [ ] Configure CORS properly
- [ ] Validate model checksums
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Security scan completed
- [ ] Penetration test passed

### Production Hardening

- [ ] Use non-root containers
- [ ] Enable firewall
- [ ] Configure IDS/IPS
- [ ] Set up WAF
- [ ] Implement network segmentation
- [ ] Enable DDoS protection
- [ ] Configure secrets management
- [ ] Enable audit trails

## Reporting Security Issues

To report security vulnerabilities, please:

1. **Do not** open public issues
2. **Email**: security@yourdomain.com
3. **Include**:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested remediation

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [GDPR Official Journal](https://eur-lex.europa.eu/legal-content/EN/TXT/)
