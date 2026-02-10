# FastAPI Application
# This module contains the main FastAPI application

from fastapi import FastAPI
from src.api.routes import predict, health, auth

app = FastAPI(
    title="UPI Fraud Detection API",
    description="API for detecting fraudulent UPI transactions",
    version="1.0.0"
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "message": "UPI Fraud Detection API",
        "version": "1.0.0"
    }
