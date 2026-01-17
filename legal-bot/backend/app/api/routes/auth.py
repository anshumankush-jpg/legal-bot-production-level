"""Authentication API routes."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User, UserRole, AuditLog
from app.services.auth_service import get_auth_service, AuthService
from app.services.password_reset_service import get_password_reset_service
from app.services.oauth_service import get_oauth_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()


# Request/Response Models

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole = UserRole.CLIENT


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class OAuthStartRequest(BaseModel):
    intended_role: UserRole = UserRole.CLIENT


class OAuthExchangeRequest(BaseModel):
    code: str
    code_verifier: str
    state: str  # For validation
    intended_role: UserRole = UserRole.CLIENT


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: str


# Helper Functions

def user_to_dict(user: User) -> dict:
    """Convert User object to dictionary."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.value if isinstance(user.role, UserRole) else user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_provisioned": user.is_provisioned,
        "created_at": user.created_at.isoformat()
    }


def raise_not_provisioned(email: str):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "NOT_PROVISIONED",
            "message": "Account not found or not provisioned. Please request access."
        }
    )


def log_audit(db: Session, user_id: Optional[str], action_type: str, details: dict, request: Request):
    """Log an audit event."""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            action_details=details,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        # Don't fail the request if audit logging fails
        print(f"Failed to log audit: {e}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    """
    auth_service = get_auth_service()
    
    try:
        token = credentials.credentials
        payload = auth_service.verify_access_token(token)
        user_id = payload.get("sub")
        
        user = auth_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


# Password Auth Endpoints

@router.post("/register", response_model=AuthResponse)
async def register(
    request_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Self-signup disabled. Only provisioned accounts can access."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "SELF_SIGNUP_DISABLED",
            "message": "Self-signup is disabled. Please request access."
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password."""
    auth_service = get_auth_service()
    user_record = auth_service.get_user_by_email(db, request_data.email)
    if not user_record or not user_record.is_provisioned:
        log_audit(db, None, "AUTH_LOGIN_DENIED", {"email": request_data.email, "reason": "not_provisioned"}, request)
        raise_not_provisioned(request_data.email)
    
    # Authenticate
    user = auth_service.authenticate_user(
        db=db,
        email=request_data.email,
        password=request_data.password
    )
    
    if not user:
        # Log failed attempt
        log_audit(db, None, "AUTH_LOGIN_FAILED", {"email": request_data.email}, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_provisioned:
        log_audit(db, user.id, "AUTH_LOGIN_DENIED", {"email": user.email, "reason": "not_provisioned"}, request)
        raise_not_provisioned(user.email)
    
    # Generate tokens
    access_token = auth_service.generate_access_token(user)
    refresh_token_str, _ = auth_service.create_refresh_token(
        db=db,
        user=user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    # Log audit
    log_audit(db, user.id, "AUTH_LOGIN_PASSWORD", {"email": user.email}, request)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user": user_to_dict(user)
    }


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    auth_service = get_auth_service()
    
    # Verify refresh token
    refresh_token = auth_service.verify_refresh_token(db, request_data.refresh_token)
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = auth_service.get_user_by_id(db, refresh_token.user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Rotate refresh token
    new_refresh_token_str, _ = auth_service.rotate_refresh_token(
        db=db,
        old_token=refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    # Generate new access token
    access_token = auth_service.generate_access_token(user)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_str,
        "token_type": "bearer",
        "user": user_to_dict(user)
    }


@router.post("/logout")
async def logout(
    request_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout (revoke refresh token)."""
    auth_service = get_auth_service()
    
    # Verify and revoke refresh token
    refresh_token = auth_service.verify_refresh_token(db, request_data.refresh_token)
    
    if refresh_token:
        auth_service.revoke_refresh_token(db, refresh_token)
    
    # Log audit
    log_audit(db, current_user.id, "AUTH_LOGOUT", {}, Request)
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(**user_to_dict(current_user))


@router.post("/change-password")
async def change_password(
    request_data: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    auth_service = get_auth_service()
    
    auth_service.change_password(
        db=db,
        user=current_user,
        old_password=request_data.old_password,
        new_password=request_data.new_password
    )
    
    # Log audit
    log_audit(db, current_user.id, "PASSWORD_CHANGED", {}, request)
    
    return {"message": "Password changed successfully"}


# Password Reset Endpoints

@router.post("/forgot-password")
async def forgot_password(
    request_data: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset (always returns 200 for security)."""
    password_reset_service = get_password_reset_service()
    
    # Get user
    auth_service = get_auth_service()
    user = auth_service.get_user_by_email(db, request_data.email)
    
    if user:
        # Create reset token
        reset_token = password_reset_service.create_reset_token(db, user)
        
        # Send email
        password_reset_service.send_reset_email(user.email, reset_token)
        
        # Log audit
        log_audit(db, user.id, "PASSWORD_RESET_REQUESTED", {"email": user.email}, request)
    
    # Always return success to prevent email enumeration
    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/reset-password")
async def reset_password(
    request_data: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Reset password using reset token."""
    password_reset_service = get_password_reset_service()
    
    password_reset_service.reset_password(
        db=db,
        token_string=request_data.token,
        new_password=request_data.new_password
    )
    
    # Get user for audit log
    reset_token = password_reset_service.verify_reset_token(db, request_data.token)
    if reset_token:
        log_audit(db, reset_token.user_id, "PASSWORD_RESET_COMPLETED", {}, request)
    
    return {"message": "Password reset successfully"}


# OAuth Endpoints

@router.get("/oauth/{provider}/start")
async def oauth_start(
    provider: str,
    intended_role: str = "client",
    db: Session = Depends(get_db)
):
    """
    Start OAuth flow.
    Returns authorization URL and PKCE parameters.
    Client should:
    1. Store code_verifier and state in sessionStorage
    2. Redirect user to auth_url
    """
    oauth_service = get_oauth_service()
    
    # Validate role
    try:
        role = UserRole(intended_role.lower())
    except ValueError:
        role = UserRole.CLIENT
    
    # Generate PKCE and state
    code_verifier, code_challenge = oauth_service.generate_pkce_pair()
    state = oauth_service.generate_state()
    
    # Get authorization URL
    if provider.lower() == "google":
        auth_url = oauth_service.get_google_auth_url(state, code_challenge)
    elif provider.lower() == "microsoft":
        auth_url = oauth_service.get_microsoft_auth_url(state, code_challenge)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    return {
        "auth_url": auth_url,
        "code_verifier": code_verifier,
        "state": state,
        "provider": provider.lower()
    }


@router.post("/oauth/{provider}/exchange", response_model=AuthResponse)
async def oauth_exchange(
    provider: str,
    request_data: OAuthExchangeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Exchange OAuth authorization code for tokens - LOGIN ONLY.
    
    CRITICAL: Only users in allowlist can login.
    Returns 403 if user not found in our database.
    """
    oauth_service = get_oauth_service()
    
    # Authenticate with provider
    if provider.lower() == "google":
        user = await oauth_service.authenticate_google(
            db=db,
            code=request_data.code,
            code_verifier=request_data.code_verifier,
            intended_role=request_data.intended_role
        )
    elif provider.lower() == "microsoft":
        user = await oauth_service.authenticate_microsoft(
            db=db,
            code=request_data.code,
            code_verifier=request_data.code_verifier,
            intended_role=request_data.intended_role
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    # Check if user is in allowlist
    if not user:
        # ACCESS DENIED - User not in allowlist
        log_audit(db, None, "AUTH_LOGIN_DENIED", {
            "provider": provider,
            "reason": "not_in_allowlist"
        }, request)
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NOT_PROVISIONED",
                "message": "Account not found or not provisioned. Please request access."
            }
        )

    if not user.is_provisioned:
        log_audit(db, user.id, "AUTH_LOGIN_DENIED", {
            "provider": provider,
            "reason": "not_provisioned"
        }, request)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NOT_PROVISIONED",
                "message": "Account not found or not provisioned. Please request access."
            }
        )
    
    # Generate tokens
    auth_service = get_auth_service()
    access_token = auth_service.generate_access_token(user)
    refresh_token_str, _ = auth_service.create_refresh_token(
        db=db,
        user=user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    # Log audit
    log_audit(db, user.id, "AUTH_LOGIN_OAUTH", {"provider": provider, "email": user.email}, request)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user": user_to_dict(user)
    }
