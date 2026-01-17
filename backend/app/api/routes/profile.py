"""Profile management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.services.profile_service import get_profile_service, ProfileService
from app.models.schemas import (
    UserProfileSchema, UserConsentSchema, UserProfileUpdate, UserConsentUpdate,
    SignedUrlResponse, AccessRequestCreate, AccessRequestResponse
)
from app.api.dependencies.auth import get_current_user
from app.models.db_models import User, AccessRequest, UserProfile
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["profile"])


# ============================================
# RESPONSE MODELS
# ============================================

class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: Optional[str] = None
    role: str
    lawyer_status: str
    is_provisioned: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MeResponse(BaseModel):
    """Response model for /api/me endpoint."""
    user: UserResponse
    profile: UserProfileSchema


# ============================================
# ME ENDPOINT
# ============================================

@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """
    Get current user info and profile.
    Returns user details and profile in a single call.
    """
    # Get or create user profile
    user_profile = profile_service.get_user_profile(db, current_user.id)
    
    if not user_profile:
        # Create a basic profile if none exists
        user_profile = UserProfile(
            user_id=current_user.id,
            display_name=current_user.name
        )
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
    
    return MeResponse(
        user=UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            lawyer_status=current_user.lawyer_status.value if hasattr(current_user.lawyer_status, 'value') else str(current_user.lawyer_status),
            is_provisioned=current_user.is_provisioned if hasattr(current_user, 'is_provisioned') else True,
            created_at=current_user.created_at,
            last_login_at=current_user.last_login_at
        ),
        profile=user_profile
    )


# ============================================
# LOGOUT ENDPOINTS
# ============================================

@router.post("/logout")
def logout(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    Clears session cookie if using cookie-based auth.
    """
    # Clear session cookie if present
    response.delete_cookie("session_id", path="/")
    response.delete_cookie("auth_token", path="/")
    
    logger.info(f"User {current_user.email} logged out")
    return {"message": "Logged out successfully"}


@router.post("/logout/all")
def logout_all_devices(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices.
    Invalidates all refresh tokens for the user.
    """
    from app.models.db_models import RefreshToken
    
    # Delete all refresh tokens for this user
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).delete()
    db.commit()
    
    # Clear session cookie
    response.delete_cookie("session_id", path="/")
    response.delete_cookie("auth_token", path="/")
    
    logger.info(f"User {current_user.email} logged out from all devices")
    return {"message": "Logged out from all devices successfully"}

@router.get("/profile", response_model=UserProfileSchema)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Retrieve the current user's profile."""
    user_profile = profile_service.get_user_profile(db, current_user.id)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
    return user_profile

@router.put("/profile", response_model=UserProfileSchema)
def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update the current user's profile."""
    updated_profile = profile_service.update_user_profile(db, current_user.id, profile_update.dict(exclude_unset=True))
    return updated_profile

@router.post("/avatar/upload-url", response_model=SignedUrlResponse)
def get_avatar_upload_url(
    filename: str = Form(..., description="Avatar filename"),
    content_type: str = Form(..., description="MIME content type (image/jpeg, image/png, etc.)"),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get a signed URL to upload an avatar image to GCS."""
    try:
        response = profile_service.get_avatar_upload_signed_url(current_user.id, filename, content_type)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to generate signed URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate signed URL: {e}")

@router.put("/profile/avatar", response_model=UserProfileSchema)
def update_profile_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update the user's avatar URL after successful upload."""
    updated_profile = profile_service.update_avatar_url(db, current_user.id, avatar_url)
    return updated_profile

@router.get("/consent", response_model=UserConsentSchema)
def get_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Retrieve the current user's consent settings."""
    user_consent = profile_service.get_user_consent(db, current_user.id)
    return user_consent

@router.put("/consent", response_model=UserConsentSchema)
def update_consent(
    consent_update: UserConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update the current user's consent settings."""
    updated_consent = profile_service.update_user_consent(db, current_user.id, consent_update.dict(exclude_unset=True))
    return updated_consent

@router.get("/profile/check-username/{username}")
def check_username_availability(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a username is available."""
    # Check format
    import re
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return {"available": False, "reason": "Invalid format"}
    
    # Check if username is taken by another user
    existing_profile = db.query(UserProfile).filter(
        UserProfile.username == username,
        UserProfile.user_id != current_user.id
    ).first()
    
    if existing_profile:
        return {"available": False, "reason": "Already taken"}
    
    return {"available": True}


@router.put("/profile/preferences")
def update_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update user preferences (stores in preferences_json field)."""
    user_profile = profile_service.get_user_profile(db, current_user.id)
    
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
    
    # Merge new preferences with existing ones
    current_prefs = user_profile.preferences_json or {}
    updated_prefs = {**current_prefs, **preferences}
    
    # Update profile with new preferences
    updated_profile = profile_service.update_user_profile(
        db, 
        current_user.id, 
        {"preferences_json": updated_prefs}
    )
    
    return {"preferences": updated_profile.preferences_json, "profile": updated_profile}


@router.post("/request-access", response_model=AccessRequestResponse)
def request_access(
    request_data: AccessRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request access for a non-provisioned user."""
    # Check if user is already provisioned
    if current_user.is_provisioned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already provisioned"
        )

    # Check if request already exists
    existing_request = db.query(AccessRequest).filter(
        AccessRequest.email == current_user.email
    ).first()

    if existing_request:
        # Update existing request
        for key, value in request_data.dict().items():
            if hasattr(existing_request, key):
                setattr(existing_request, key, value)
        db.add(existing_request)
        db.commit()
        db.refresh(existing_request)
        access_request = existing_request
    else:
        # Create new request
        access_request = AccessRequest(
            email=current_user.email,
            name=request_data.name,
            requested_role=request_data.requested_role,
            reason=request_data.reason,
            organization=request_data.organization
        )
        db.add(access_request)
        db.commit()
        db.refresh(access_request)

    logger.info(f"Access request created/updated for {current_user.email}")
    return access_request