"""FastAPI dependencies for authentication and authorization."""
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.db_models import User, UserRole

# HTTP Bearer token scheme (for Authorization header)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Supports both Authorization header and HttpOnly cookie.
    """
    token = None
    
    # Try Authorization header first
    if authorization:
        token = authorization.credentials
    # Fall back to cookie
    elif access_token:
        token = access_token
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode token
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (alias for clarity)."""
    return current_user


async def get_optional_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    try:
        return await get_current_user(authorization, access_token, db)
    except HTTPException:
        return None


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access control.
    Usage: require_role(UserRole.ADMIN, UserRole.LAWYER)
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    
    return role_checker


def require_provisioned(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be provisioned (completed setup)."""
    if not current_user.is_provisioned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account setup not completed. Please complete provisioning."
        )
    return current_user
