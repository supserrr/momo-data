"""
Basic Authentication Module for Assignment Requirements
This module provides Basic Authentication for the MoMo Data Processing System API.
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create Basic Auth security instance
security = HTTPBasic()

# Default credentials for assignment (in production, use environment variables)
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password"

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify Basic Authentication credentials.
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        str: Username if authentication successful
        
    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid
    """
    try:
        # Use secrets.compare_digest to prevent timing attacks
        correct_username = secrets.compare_digest(credentials.username, DEFAULT_USERNAME)
        correct_password = secrets.compare_digest(credentials.password, DEFAULT_PASSWORD)
        
        if not (correct_username and correct_password):
            logger.warning(f"Authentication failed for user: {credentials.username}")
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        
        logger.info(f"Authentication successful for user: {credentials.username}")
        return credentials.username
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Basic"},
        )

def get_optional_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Optional authentication for endpoints that can work with or without auth.
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        str or None: Username if authentication successful, None otherwise
    """
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

def get_current_user_with_auto_auth(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """
    Enhanced authentication that automatically authenticates requests from localhost:3000.
    
    Args:
        request: FastAPI request object
        credentials: HTTP Basic Auth credentials
        
    Returns:
        str: Username if authentication successful
        
    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid
    """
    try:
        # Check if request is from localhost:3000 (frontend)
        client_host = request.client.host if request.client else None
        referer = request.headers.get("referer", "")
        origin = request.headers.get("origin", "")
        user_agent = request.headers.get("user-agent", "")
        
        # More comprehensive auto-authentication logic
        is_localhost = client_host in ["127.0.0.1", "localhost", "::1", "0.0.0.0"]
        is_frontend_request = (
            "localhost:3000" in referer or 
            "127.0.0.1:3000" in referer or
            "localhost:3000" in origin or
            "127.0.0.1:3000" in origin or
            "Mozilla" in user_agent  # Browser request
        )
        
        # Auto-authenticate requests from frontend
        if is_localhost and is_frontend_request:
            logger.info(f"Auto-authenticating request from frontend: {client_host}, referer: {referer}")
            return DEFAULT_USERNAME
        
        # For other requests, use normal authentication
        return get_current_user(credentials)
        
    except Exception as e:
        logger.error(f"Authentication error in auto-auth: {str(e)}")
        # Fall back to normal authentication
        return get_current_user(credentials)
