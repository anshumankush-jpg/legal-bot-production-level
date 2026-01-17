"""Authentication API endpoints."""
import secrets
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db
from app.core.deps import get_current_user, get_optional_user
from app.core.config import settings
from app.models.db_models import User, UserRole, OAuthProvider
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# ============================================
# REQUEST/RESPONSE SCHEMAS
# ============================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None
    role: Optional[str] = "client"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class OAuthStateResponse(BaseModel):
    auth_url: str
    state: str


# ============================================
# EMAIL/PASSWORD AUTH
# ============================================

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    req: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Register a new user with email and password."""
    try:
        # Validate role
        try:
            user_role = UserRole(request.role)
        except ValueError:
            user_role = UserRole.CLIENT
        
        # Create user
        user = AuthService.create_user(
            db=db,
            email=request.email,
            password=request.password,
            name=request.name,
            role=user_role
        )
        
        # Create tokens
        access_token, refresh_token = AuthService.create_user_tokens(
            db=db,
            user=user,
            user_agent=req.headers.get("user-agent"),
            ip_address=req.client.host if req.client else None
        )
        
        # Log audit
        AuthService.log_audit(
            db=db,
            action="signup",
            user_id=user.id,
            details={"method": "email", "role": user.role.value},
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get("user-agent")
        )
        
        # Set HttpOnly cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_ACCESS_TTL_MIN * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
                "is_provisioned": user.is_provisioned
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    req: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login with email and password."""
    # Authenticate user
    user = AuthService.authenticate_user(db, request.email, request.password)
    
    if not user:
        # Log failed attempt
        AuthService.log_audit(
            db=db,
            action="login_failed",
            details={"email": request.email, "reason": "invalid_credentials"},
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get("user-agent")
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token, refresh_token = AuthService.create_user_tokens(
        db=db,
        user=user,
        user_agent=req.headers.get("user-agent"),
        ip_address=req.client.host if req.client else None
    )
    
    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Log success
    AuthService.log_audit(
        db=db,
        action="login_success",
        user_id=user.id,
        details={"method": "email"},
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent")
    )
    
    # Set HttpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TTL_MIN * 60
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_provisioned": user.is_provisioned
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        # Refresh tokens (with rotation)
        new_access_token, new_refresh_token = AuthService.refresh_access_token(
            db, request.refresh_token
        )
        
        # Update cookies
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_ACCESS_TTL_MIN * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60
        )
        
        # Decode new access token to get user info
        from app.core.security import decode_access_token
        payload = decode_access_token(new_access_token)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            user={
                "id": payload["sub"],
                "email": payload["email"],
                "name": payload.get("name"),
                "role": payload["role"]
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Logout and revoke refresh token."""
    if refresh_token:
        AuthService.revoke_refresh_token(db, refresh_token)
    
    # Log audit
    if current_user:
        AuthService.log_audit(
            db=db,
            action="logout",
            user_id=current_user.id
        )
    
    # Clear cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Logged out successfully"}


# ============================================
# PASSWORD RESET
# ============================================

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Request password reset token."""
    # Create reset token (returns None if user not found, but we don't reveal that)
    token = AuthService.create_password_reset(db, request.email)
    
    # TODO: Send email with reset link
    # For now, return token in response (DEVELOPMENT ONLY)
    if settings.DEBUG and token:
        return {
            "message": "Password reset email sent",
            "reset_token": token  # REMOVE IN PRODUCTION
        }
    
    return {"message": "If your email is registered, you will receive a password reset link"}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using reset token."""
    AuthService.reset_password(db, request.token, request.new_password)
    return {"message": "Password reset successful"}


# ============================================
# GOOGLE OAUTH
# ============================================

@router.get("/google/login", response_model=OAuthStateResponse)
async def google_login():
    """Initiate Google OAuth flow."""
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Get authorization URL
        auth_url = OAuthService.get_google_auth_url(state)
        
        return OAuthStateResponse(auth_url=auth_url, state=state)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    req: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback."""
    try:
        # Exchange code for user info
        provider_user_id, email, name, picture = await OAuthService.handle_google_oauth(code)
        
        # Get or create user
        user = AuthService.get_or_create_oauth_user(
            db=db,
            provider=OAuthProvider.GOOGLE,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
            picture=picture
        )
        
        # Create tokens
        access_token, refresh_token = AuthService.create_user_tokens(
            db=db,
            user=user,
            user_agent=req.headers.get("user-agent"),
            ip_address=req.client.host if req.client else None
        )
        
        # Log audit
        AuthService.log_audit(
            db=db,
            action="oauth_login",
            user_id=user.id,
            details={"provider": "google"},
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get("user-agent")
        )
        
        # Set cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_ACCESS_TTL_MIN * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60
        )
        
        # Redirect to frontend
        redirect_url = f"{settings.FRONTEND_BASE_URL}/chat?auth=success"
        return RedirectResponse(url=redirect_url)
    
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        redirect_url = f"{settings.FRONTEND_BASE_URL}/login?error=oauth_failed"
        return RedirectResponse(url=redirect_url)


# ============================================
# MICROSOFT OAUTH
# ============================================

@router.get("/microsoft/login", response_model=OAuthStateResponse)
async def microsoft_login():
    """Initiate Microsoft OAuth flow."""
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Get authorization URL
        auth_url = OAuthService.get_microsoft_auth_url(state)
        
        return OAuthStateResponse(auth_url=auth_url, state=state)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str,
    state: str,
    req: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Handle Microsoft OAuth callback."""
    try:
        # Exchange code for user info
        provider_user_id, email, name, picture = await OAuthService.handle_microsoft_oauth(code)
        
        # Get or create user
        user = AuthService.get_or_create_oauth_user(
            db=db,
            provider=OAuthProvider.MICROSOFT,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
            picture=picture
        )
        
        # Create tokens
        access_token, refresh_token = AuthService.create_user_tokens(
            db=db,
            user=user,
            user_agent=req.headers.get("user-agent"),
            ip_address=req.client.host if req.client else None
        )
        
        # Log audit
        AuthService.log_audit(
            db=db,
            action="oauth_login",
            user_id=user.id,
            details={"provider": "microsoft"},
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get("user-agent")
        )
        
        # Set cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_ACCESS_TTL_MIN * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60
        )
        
        # Redirect to frontend
        redirect_url = f"{settings.FRONTEND_BASE_URL}/chat?auth=success"
        return RedirectResponse(url=redirect_url)
    
    except Exception as e:
        logger.error(f"Microsoft OAuth callback error: {str(e)}")
        redirect_url = f"{settings.FRONTEND_BASE_URL}/login?error=oauth_failed"
        return RedirectResponse(url=redirect_url)


# ============================================
# CURRENT USER
# ============================================

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user info."""
    from app.models.db_models import UserProfile
    
    # Get profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "display_name": profile.display_name if profile else current_user.name,
        "role": current_user.role.value,
        "lawyer_status": current_user.lawyer_status.value,
        "is_provisioned": current_user.is_provisioned,
        "is_verified": current_user.is_verified,
        "avatar_url": profile.avatar_url if profile else None,
        "preferences": profile.preferences_json if profile else {}
    }
