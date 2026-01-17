"""
User preferences management endpoints for LEGID
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.api.routes.auth_v2 import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/preferences", tags=["preferences"])

# Request/Response Models
class PreferencesResponse(BaseModel):
    user_id: str
    theme: str = "dark"
    font_size: str = "medium"
    response_style: str = "detailed"
    language: str = "en"
    auto_read_responses: bool = False
    law_category: Optional[str] = None
    jurisdiction: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = "CA"

class PreferencesUpdate(BaseModel):
    theme: Optional[str] = None
    font_size: Optional[str] = None
    response_style: Optional[str] = None
    language: Optional[str] = None
    auto_read_responses: Optional[bool] = None
    law_category: Optional[str] = None
    jurisdiction: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None

# Mock database
MOCK_PREFERENCES = {}

@router.get("", response_model=PreferencesResponse)
async def get_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get user preferences"""
    try:
        user_id = current_user['user_id']
        
        # Get or create default preferences
        if user_id not in MOCK_PREFERENCES:
            MOCK_PREFERENCES[user_id] = {
                "user_id": user_id,
                "theme": "dark",
                "font_size": "medium",
                "response_style": "detailed",
                "language": "en",
                "auto_read_responses": False,
                "country": "CA"
            }

        return PreferencesResponse(**MOCK_PREFERENCES[user_id])

    except Exception as e:
        logger.error(f"Failed to get preferences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get preferences")

@router.put("", response_model=PreferencesResponse)
async def update_preferences(
    request: PreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        user_id = current_user['user_id']
        
        # Get current preferences or create defaults
        if user_id not in MOCK_PREFERENCES:
            MOCK_PREFERENCES[user_id] = {
                "user_id": user_id,
                "theme": "dark",
                "font_size": "medium",
                "response_style": "detailed",
                "language": "en",
                "auto_read_responses": False,
                "country": "CA"
            }

        # Update with new values
        current_prefs = MOCK_PREFERENCES[user_id]
        update_data = request.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            if value is not None:
                current_prefs[key] = value

        return PreferencesResponse(**current_prefs)

    except Exception as e:
        logger.error(f"Failed to update preferences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update preferences")
