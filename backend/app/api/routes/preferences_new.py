"""User preferences API endpoints."""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.db_models import User, UserProfile

router = APIRouter(prefix="/api/preferences", tags=["preferences"])

# ============================================
# REQUEST/RESPONSE SCHEMAS
# ============================================

class PreferencesResponse(BaseModel):
    theme: Optional[str] = "dark"
    fontSize: Optional[str] = "medium"
    responseStyle: Optional[str] = "balanced"
    language: Optional[str] = "en"
    autoReadResponses: Optional[bool] = False


class PreferencesUpdate(BaseModel):
    theme: Optional[str] = None
    fontSize: Optional[str] = None
    responseStyle: Optional[str] = None
    language: Optional[str] = None
    autoReadResponses: Optional[bool] = None


# ============================================
# PREFERENCES ENDPOINTS
# ============================================

@router.get("", response_model=PreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences."""
    # Get user profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create default profile
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Extract preferences from JSON
    prefs = profile.preferences_json or {}
    
    return PreferencesResponse(
        theme=prefs.get("theme", "dark"),
        fontSize=prefs.get("fontSize", "medium"),
        responseStyle=prefs.get("responseStyle", "balanced"),
        language=prefs.get("language", "en"),
        autoReadResponses=prefs.get("autoReadResponses", False)
    )


@router.put("", response_model=PreferencesResponse)
async def update_preferences(
    request: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences."""
    # Get user profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create profile
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()
    
    # Get current preferences
    prefs = profile.preferences_json or {}
    
    # Update only provided fields
    update_data = request.dict(exclude_unset=True)
    prefs.update(update_data)
    
    # Save
    profile.preferences_json = prefs
    db.commit()
    db.refresh(profile)
    
    return PreferencesResponse(
        theme=prefs.get("theme", "dark"),
        fontSize=prefs.get("fontSize", "medium"),
        responseStyle=prefs.get("responseStyle", "balanced"),
        language=prefs.get("language", "en"),
        autoReadResponses=prefs.get("autoReadResponses", False)
    )


@router.post("/reset")
async def reset_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset preferences to defaults."""
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    if profile:
        profile.preferences_json = {
            "theme": "dark",
            "fontSize": "medium",
            "responseStyle": "balanced",
            "language": "en",
            "autoReadResponses": False
        }
        db.commit()
    
    return {"message": "Preferences reset to defaults"}
