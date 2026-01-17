"""
Authentication dependencies for FastAPI routes.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.models.db_models import User
from app.services.auth_service import get_current_user as auth_get_current_user

logger = logging.getLogger(__name__)

# OAuth2 Bearer token security
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Supports both Authorization header (Bearer token) and authorization header.
    Falls back to dev mode if no token provided (for local development).
    """
    token = None

    # Try to get token from HTTPBearer
    if credentials:
        token = credentials.credentials
    # Try to get from authorization header directly
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")

    if not token:
        # In dev mode, allow requests without token (will use dev-user-001)
        # In production, this should raise an error
        logger.warning("No authentication token provided - using dev mode")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a Bearer token in Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await auth_get_current_user(token, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work with or without authentication.
    """
    try:
        return await get_current_user(credentials, authorization, db)
    except HTTPException:
        return None
