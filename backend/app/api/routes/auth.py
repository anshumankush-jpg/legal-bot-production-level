"""
Authentication Routes for LegalAI
Handles user registration, session creation, and profile management
"""
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request, Response, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta

from app.auth.firebase_auth import get_firebase_auth
from app.auth.bigquery_client import get_bigquery_client
from app.middleware.auth_middleware import get_current_user, get_optional_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SessionRequest(BaseModel):
    """Request to create a session from Firebase ID token"""
    idToken: str = Field(..., description="Firebase ID token from client")
    role: Optional[str] = Field(None, description="User role (customer|lawyer) - only for first-time signup")


class SessionResponse(BaseModel):
    """Session creation response"""
    user_id: str
    email: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    lawyer_status: Optional[str] = None
    needs_role_selection: bool = False
    needs_onboarding: bool = False
    photo_url: Optional[str] = None


class SetRoleRequest(BaseModel):
    """Request to set user role (first-time users)"""
    role: str = Field(..., description="customer|lawyer")


class UserProfile(BaseModel):
    """User profile response"""
    user_id: str
    email: str
    display_name: Optional[str]
    photo_url: Optional[str]
    role: str
    lawyer_status: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_session_cookie(user_data: dict, env: str = 'dev') -> str:
    """
    Create secure session cookie (simplified JWT for now)
    In production, use proper JWT signing with secret key
    """
    import json
    import base64
    
    # In production, sign this with JWT secret
    session_data = {
        'user_id': user_data['user_id'],
        'email': user_data['email'],
        'role': user_data.get('role'),
        'lawyer_status': user_data.get('lawyer_status'),
        'env': env,
        'exp': (datetime.utcnow() + timedelta(days=7)).isoformat()
    }
    
    # TODO: Replace with proper JWT signing
    # For now, just base64 encode (NOT SECURE - implement JWT)
    session_json = json.dumps(session_data)
    session_token = base64.b64encode(session_json.encode()).decode()
    
    return session_token


def get_env_from_request(request: Request) -> str:
    """Determine environment from request origin"""
    origin = request.headers.get('origin', '')
    referer = request.headers.get('referer', '')
    
    if 'localhost' in origin or 'localhost' in referer:
        return 'dev'
    elif 'dev.' in origin or 'dev.' in referer:
        return 'dev'
    else:
        return 'prod'


# ============================================================================
# AUTH ROUTES
# ============================================================================

@router.post("/session", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def create_session(
    request: Request,
    response: Response,
    session_req: SessionRequest
):
    """
    Create authenticated session from Firebase ID token.
    
    This is the CORE authentication endpoint that:
    1. Verifies Firebase ID token
    2. Creates or finds internal user_id
    3. Issues secure session cookie with managed identity
    4. Logs login event to BigQuery
    
    Returns user profile and flags for onboarding/role selection.
    """
    firebase = get_firebase_auth()
    bq_client = get_bigquery_client()
    
    # Verify Firebase ID token
    firebase_user = await firebase.verify_token(session_req.idToken)
    
    if not firebase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired ID token"
        )
    
    auth_uid = firebase_user['uid']
    auth_provider = firebase_user['provider']
    email = firebase_user['email']
    display_name = firebase_user.get('name')
    photo_url = firebase_user.get('picture')
    is_verified = firebase_user.get('email_verified', False)
    
    # Determine environment
    env = get_env_from_request(request)
    
    # Get or create user_id (MANAGED IDENTITY)
    user_id = await bq_client.get_user_id(auth_uid, auth_provider)
    
    if not user_id:
        # New user - create internal identity
        # Determine role
        if session_req.role and session_req.role in ['customer', 'lawyer']:
            role = session_req.role
        else:
            role = None  # Will prompt for role selection
        
        # Determine lawyer_status
        if role == 'lawyer':
            lawyer_status = 'pending'
        else:
            lawyer_status = 'not_applicable'
        
        # Upsert to BigQuery
        user_id = await bq_client.upsert_identity_user(
            auth_uid=auth_uid,
            auth_provider=auth_provider,
            email=email,
            role=role or 'customer',  # Default to customer if not specified
            display_name=display_name,
            photo_url=photo_url,
            is_verified=is_verified,
            lawyer_status=lawyer_status
        )
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user identity"
            )
        
        needs_role_selection = (role is None)
        needs_onboarding = (role == 'lawyer')
    else:
        # Existing user - get profile
        user_profile = await bq_client.get_user_by_id(user_id)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User profile not found"
            )
        
        role = user_profile.get('role')
        lawyer_status = user_profile.get('lawyer_status')
        needs_role_selection = False
        needs_onboarding = False
        
        # Update last login
        await bq_client.upsert_identity_user(
            auth_uid=auth_uid,
            auth_provider=auth_provider,
            email=email,
            role=role,
            display_name=display_name,
            photo_url=photo_url,
            is_verified=is_verified,
            lawyer_status=lawyer_status
        )
    
    # Log login event
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get('user-agent')
    
    await bq_client.log_login_event(
        user_id=user_id,
        auth_provider=auth_provider,
        event_type='login',
        success=True,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Create session cookie (MANAGED IDENTITY)
    session_data = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'lawyer_status': lawyer_status
    }
    
    session_token = create_session_cookie(session_data, env)
    
    # Set HttpOnly secure cookie
    is_prod = (env == 'prod')
    response.set_cookie(
        key="legalai_session",
        value=session_token,
        httponly=True,  # Prevent JS access
        secure=is_prod,  # HTTPS only in production
        samesite="strict" if is_prod else "lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        domain=None  # Current domain
    )
    
    # Return user profile
    return SessionResponse(
        user_id=user_id,
        email=email,
        display_name=display_name,
        role=role,
        lawyer_status=lawyer_status,
        needs_role_selection=needs_role_selection,
        needs_onboarding=needs_onboarding,
        photo_url=photo_url
    )


@router.post("/set-role", response_model=SessionResponse)
async def set_user_role(
    request: Request,
    response: Response,
    role_req: SetRoleRequest,
    user: dict = Depends(get_current_user)
):
    """
    Set user role (first-time users only).
    Called after initial login if needs_role_selection = true.
    """
    bq_client = get_bigquery_client()
    
    # Validate role
    if role_req.role not in ['customer', 'lawyer']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'customer' or 'lawyer'"
        )
    
    # Check if user already has a role
    if user.get('role') and user['role'] != 'customer':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already set and cannot be changed"
        )
    
    # Set lawyer_status
    lawyer_status = 'pending' if role_req.role == 'lawyer' else 'not_applicable'
    
    # Update in BigQuery
    success = await bq_client.update_user_role(
        user_id=user['user_id'],
        role=role_req.role,
        lawyer_status=lawyer_status
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )
    
    # Update session cookie
    user['role'] = role_req.role
    user['lawyer_status'] = lawyer_status
    
    env = get_env_from_request(request)
    session_token = create_session_cookie(user, env)
    
    is_prod = (env == 'prod')
    response.set_cookie(
        key="legalai_session",
        value=session_token,
        httponly=True,
        secure=is_prod,
        samesite="strict" if is_prod else "lax",
        max_age=7 * 24 * 60 * 60
    )
    
    needs_onboarding = (role_req.role == 'lawyer')
    
    return SessionResponse(
        user_id=user['user_id'],
        email=user['email'],
        display_name=user.get('display_name'),
        role=role_req.role,
        lawyer_status=lawyer_status,
        needs_role_selection=False,
        needs_onboarding=needs_onboarding,
        photo_url=user.get('photo_url')
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user profile.
    
    Reads from server session - NEVER accepts user_id from client.
    """
    return UserProfile(
        user_id=user['user_id'],
        email=user['email'],
        display_name=user.get('display_name'),
        photo_url=user.get('photo_url'),
        role=user.get('role', 'customer'),
        lawyer_status=user.get('lawyer_status'),
        is_active=user.get('is_active', True),
        is_verified=user.get('is_verified', False),
        created_at=user.get('created_at', datetime.utcnow()),
        last_login_at=user.get('last_login_at')
    )


@router.post("/logout")
async def logout(
    response: Response,
    user: dict = Depends(get_optional_user)
):
    """
    Logout user by clearing session cookie.
    """
    firebase = get_firebase_auth()
    bq_client = get_bigquery_client()
    
    # Log logout event
    if user:
        await bq_client.log_login_event(
            user_id=user['user_id'],
            auth_provider=user.get('auth_provider', 'unknown'),
            event_type='logout',
            success=True
        )
        
        # Optionally revoke Firebase refresh tokens
        if user.get('auth_uid'):
            await firebase.revoke_refresh_tokens(user['auth_uid'])
    
    # Clear session cookie
    response.delete_cookie("legalai_session")
    
    return {"message": "Logged out successfully"}


@router.get("/health")
async def auth_health():
    """Health check for auth system"""
    firebase = get_firebase_auth()
    bq_client = get_bigquery_client()
    
    return {
        "status": "healthy",
        "firebase_initialized": firebase.initialized,
        "bigquery_available": bq_client.client is not None
    }
