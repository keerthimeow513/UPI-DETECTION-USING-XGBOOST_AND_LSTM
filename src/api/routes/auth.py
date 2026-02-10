# Authentication Routes
# This module contains the /auth endpoints

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from src.api.schemas import TokenRequest, TokenResponse
from src.core.security import verify_credentials, create_access_token
from datetime import timedelta

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/token", response_model=TokenResponse)
async def login(request: TokenRequest):
    """
    Authenticate user and return access token
    
    Args:
        request: Username and password
        
    Returns:
        JWT access token
    """
    user = verify_credentials(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800
    }


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user
    
    Args:
        token: JWT token
        
    Returns:
        Current user information
    """
    # TODO: Implement user retrieval from token
    return {"username": "current_user", "role": "user"}
