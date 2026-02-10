# Deployment Guide

Comprehensive deployment guide for the UPI Fraud Detection System.

## Overview

This guide covers deployment strategies for development, staging, and production environments. The system can be deployed using Docker containers or directly on virtual machines.

## Prerequisites

### Hardware Requirements

| Environment | CPU | RAM | Storage | Network |
|-------------|-----|-----|---------|---------|
| Development | 2 cores | 4 GB | 10 GB | Standard |
| Staging | 4 cores | 8 GB | 20 GB | Standard |
| Production | 8 cores | 16 GB | 50 GB | High bandwidth |

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.8+
- Redis 6.0+ (optional)
- Nginx or similar reverse proxy (production)

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### Quick Start

```bash
# Clone and navigate to project
cd UPI_FRAUD_DETECTION

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - ./02_models:/app/02_models
      - ./07_configs:/app/07_configs
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Option 2: Docker (Individual Containers)

#### Build API Image

```bash
# Build API image
docker build -t upi-fraud-api .

# Run API container
docker run -d \
  --name upi-fraud-api \
  -p 8000:8000 \
  -v $(pwd)/02_models:/app/02_models \
  -v $(pwd)/07_configs:/app/07_configs \
  -e ENVIRONMENT=production \
  upi-fraud-api
```

#### Build Dashboard Image

```bash
# Build dashboard image
docker build -f Dockerfile.dashboard -t upi-fraud-dashboard .

# Run dashboard container
docker run -d \
  --name upi-fraud-dashboard \
  -p 8501:8501 \
  -e API_URL=http://upi-fraud-api:8000 \
  upi-fraud-dashboard
```

### Option 3: Virtual Machine Deployment

#### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start API server
cd UPI_FRAUD_DETECTION
uvicorn 04_inference.api:app --host 0.0.0.0 --port 8000 --workers 4

# In separate terminal, start dashboard
streamlit run 06_dashboard/app.py --server.port 8501
```

#### Using Systemd

Create service file `/etc/systemd/system/upi-fraud-api.service`:

```ini
[Unit]
Description=UPI Fraud Detection API
After=network.target

[Service]
Type=notify
User=upi-fraud
Group=upi-fraud
WorkingDirectory=/opt/upi-fraud-detection
Environment="PATH=/opt/upi-fraud-detection/venv/bin"
ExecStart=/opt/upi-fraud-detection/venv/bin/uvicorn 04_inference.api:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable upi-fraud-api
sudo systemctl start upi-fraud-api
sudo systemctl status upi-fraud-api
```

## Environment Configuration

### Environment Variables

#### Required Variables

```bash
# Application
ENVIRONMENT=production          # development, staging, production
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# Security
JWT_SECRET=your-secure-secret-key-min-32-chars
JWT_ALGORITHM=HS256

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/upi_fraud
```

#### Production-Specific Variables

```bash
# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/api.crt
SSL_KEY_PATH=/etc/ssl/private/api.key

# Monitoring
METRICS_ENABLED=true
SENTRY_DSN=https://xxx@sentry.io/xxx

# Rate Limiting
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/1
```

### Configuration File

Edit `07_configs/config.yaml` for production:

```yaml
paths:
  raw_data: "/data/raw/upi_transactions.csv"
  processed_data: "/data/processed/"
  artifacts: "/data/models/artifacts/"

data:
  num_users: 10000
  num_transactions: 200000
  fraud_rate: 0.02
  lookback: 10
  test_split: 0.2

model:
  lstm:
    units_1: 64
    units_2: 32
    dropout: 0.2
    epochs: 10
    batch_size: 32
    learning_rate: 0.001
  xgboost:
    n_estimators: 100
    max_depth: 5
    learning_rate: 0.1

api:
  host: "0.0.0.0"
  port: 8000

security:
  known_safe_devices:
    - "device_id_1"
    - "device_id_2"
  risk_thresholds:
    block: 0.8
    flag: 0.5
  amount_thresholds:
    high: 10000
    critical: 50000
  unusual_hours:
    start: 0
    end: 5
  velocity_thresholds:
    transactions_per_hour: 5
    amount_per_hour: 50000

logging:
  level: INFO
  format: json
  output: /var/log/upi-fraud/
```

## Production Checklist

### Security Hardening

- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up fail2ban
- [ ] Enable audit logging
- [ ] Implement network segmentation
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up API authentication

### Monitoring Setup

- [ ] Configure log aggregation
- [ ] Set up health checks
- [ ] Create dashboards
- [ ] Configure alerts
- [ ] Set up metrics collection
- [ ] Implement tracing

### Backup and Recovery

- [ ] Backup model artifacts
- [ ] Backup configuration
- [ ] Test recovery procedure
- [ ] Document RTO/RPO
- [ ] Implement auto-failover

### Performance Optimization

- [ ] Enable Gzip compression
- [ ] Configure connection pooling
- [ ] Optimize model inference
- [ ] Set up caching layer
- [ ] Configure load balancing

## Monitoring Setup

### Health Checks

#### API Health Endpoint

```bash
curl http://localhost:8000/
```

Response:
```json
{
    "status": "online",
    "system": "UPI Fraud Shield",
    "environment": "production",
    "version": "1.0.0"
}
```

#### Docker Health Check

```bash
docker inspect --format='{{.State.Health.Status}}' upi-fraud-api
```

### Logging Configuration

#### JSON Logging Format

```python
# In utils/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)
```

#### Log Shipping with Fluentd

```yaml
# fluentd.conf
<source>
  @type forward
  port 24224
</source>

<filter **>
  @type record_transformer
  <record>
    service upi-fraud-api
    environment production
  </record>
</filter>

<match **>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
</match>
```

### Metrics with Prometheus

```python
from prometheus_client import Counter, Histogram, start_http_server

# Start metrics server
start_http_server(8001)

# Define metrics
REQUEST_COUNT = Counter('upi_fraud_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('upi_fraud_request_latency_seconds', 'Request latency')
PREDICTION_COUNT = Counter('upi_fraud_predictions_total', 'Total predictions', ['verdict'])
```

### Alerting Rules

```yaml
# prometheus/alert_rules.yml
groups:
  - name: upi-fraud-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(upi_fraud_requests_total{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on UPI Fraud API"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(upi_fraud_request_latency_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "95th percentile latency > 1s"
```

## Scaling Considerations

### Horizontal Scaling

```
                        ┌─────────────────────────┐
                        │     Load Balancer       │
                        │     (Nginx/HAProxy)     │
                        └───────────┬─────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
    ┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐
    │   API Node 1  │      │   API Node 2  │      │   API Node N  │
    │   :8001       │      │   :8002       │      │   :800N       │
    └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   │
                        ┌──────────┴──────────┐
                        │   Redis Cluster     │
                        │   (Feature Store)   │
                        └─────────────────────┘
```

### Scaling Guidelines

| Component | Scaling Method | Max Instances |
|-----------|---------------|--------------|
| API | Horizontal (stateless) | 10+ |
| Redis | Vertical + Clustering | N/A |
| Dashboard | Horizontal | 3 |
| Models | Shared storage | N/A |

### Performance Tuning

#### API Server

```bash
# uvicorn with gunicorn
gunicorn 04_inference.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5
```

#### Model Inference Optimization

```python
# In service.py, enable model warmup
@app.on_event("startup")
async def warmup_models():
    # Warm up LSTM
    dummy_input = np.zeros((1, 10, 8))
    lstm_model.predict(dummy_input)
    
    # Warm up XGBoost
    xgb_model.predict_proba(np.zeros((1, 8)))
```

#### Redis Optimization

```redis
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
```

## Docker Image Optimization

### Multi-stage Build

```dockerfile
# Dockerfile
FROM python:3.11-slim AS builder

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

FROM python:3.11-slim AS runtime
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /home/app /home/app
WORKDIR /home/app

CMD ["uvicorn", "04_inference.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Image Size Reduction

```bash
# Use slim base image
FROM python:3.11-slim

# Remove unnecessary packages
RUN apt-get update && \
    apt-get remove -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

# Use no-install-recommends
RUN apt-get install -y --no-install-recommends <package>
```

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Configuration
BACKUP_DIR="/backup/upi-fraud"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup models
tar -czf $BACKUP_DIR/models_$DATE.tar.gz 02_models/

# Backup config
cp 07_configs/config.yaml $BACKUP_DIR/

# Upload to cloud
aws s3 cp $BACKUP_DIR s3://upi-fraud-backups/ --recursive

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Recovery Procedure

```bash
#!/bin/bash
# restore.sh

BACKUP_DATE=$1
BACKUP_DIR="/backup/upi-fraud"

# Stop services
docker-compose down

# Restore models
tar -xzf $BACKUP_DIR/models_$BACKUP_DATE.tar.gz

# Restore config
cp $BACKUP_DIR/config.yaml 07_configs/

# Start services
docker-compose up -d
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Model not loading | Missing artifacts | Run `python 03_training/train.py` |
| Connection refused | Port not exposed | Check `-p 8000:8000` |
| Redis connection error | Wrong host | Set `REDIS_HOST` env var |
| Out of memory | Model too large | Increase container memory |
| High latency | Unoptimized model | Enable model warmup |

### Debug Commands

```bash
# Check API logs
docker logs upi-fraud-api --tail 100

# Check resource usage
docker stats

# Check network
docker network ls

# Check volumes
docker volume ls

# Restart service
docker-compose restart api

# Rebuild without cache
docker-compose build --no-cache
```

## Rollback Procedure

### Docker Rollback

```bash
# View previous images
docker images | grep upi-fraud-api

# Rollback to previous version
docker-compose down
docker-compose pull upi-fraud-api:previous-tag
docker-compose up -d
```

### Configuration Rollback

```bash
# Restore previous config
git checkout HEAD~1 07_configs/config.yaml
docker-compose restart api
```
