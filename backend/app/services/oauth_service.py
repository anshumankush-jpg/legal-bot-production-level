"""OAuth service for Google and Microsoft authentication."""
import httpx
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode
from app.core.config import settings


class OAuthService:
    """Handle OAuth flows for Google and Microsoft."""
    
    # Google OAuth endpoints
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
    
    # Microsoft OAuth endpoints
    MS_AUTH_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
    MS_TOKEN_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    MS_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"
    
    @staticmethod
    def get_google_auth_url(state: str) -> str:
        """Generate Google OAuth authorization URL."""
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError("Google OAuth not configured. Missing GOOGLE_CLIENT_ID.")
        
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        return f"{OAuthService.GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    @staticmethod
    async def exchange_google_code(code: str) -> Dict[str, Any]:
        """Exchange Google authorization code for tokens."""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google OAuth not configured.")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OAuthService.GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def get_google_user_info(access_token: str) -> Dict[str, Any]:
        """Fetch Google user profile."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OAuthService.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    def get_microsoft_auth_url(state: str) -> str:
        """Generate Microsoft OAuth authorization URL."""
        if not settings.MS_CLIENT_ID:
            raise ValueError("Microsoft OAuth not configured. Missing MS_CLIENT_ID.")
        
        tenant = settings.MS_TENANT or "common"
        auth_url = OAuthService.MS_AUTH_URL_TEMPLATE.format(tenant=tenant)
        
        params = {
            "client_id": settings.MS_CLIENT_ID,
            "redirect_uri": settings.MS_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile User.Read",
            "state": state,
            "response_mode": "query"
        }
        
        return f"{auth_url}?{urlencode(params)}"
    
    @staticmethod
    async def exchange_microsoft_code(code: str) -> Dict[str, Any]:
        """Exchange Microsoft authorization code for tokens."""
        if not settings.MS_CLIENT_ID or not settings.MS_CLIENT_SECRET:
            raise ValueError("Microsoft OAuth not configured.")
        
        tenant = settings.MS_TENANT or "common"
        token_url = OAuthService.MS_TOKEN_URL_TEMPLATE.format(tenant=tenant)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": settings.MS_CLIENT_ID,
                    "client_secret": settings.MS_CLIENT_SECRET,
                    "redirect_uri": settings.MS_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def get_microsoft_user_info(access_token: str) -> Dict[str, Any]:
        """Fetch Microsoft user profile."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OAuthService.MS_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def handle_google_oauth(code: str) -> Tuple[str, str, str, Optional[str]]:
        """
        Complete Google OAuth flow.
        Returns: (provider_user_id, email, name, picture_url)
        """
        # Exchange code for tokens
        token_data = await OAuthService.exchange_google_code(code)
        access_token = token_data["access_token"]
        
        # Get user info
        user_info = await OAuthService.get_google_user_info(access_token)
        
        return (
            user_info["sub"],  # Google's unique user ID
            user_info["email"].lower(),
            user_info.get("name"),
            user_info.get("picture")
        )
    
    @staticmethod
    async def handle_microsoft_oauth(code: str) -> Tuple[str, str, str, Optional[str]]:
        """
        Complete Microsoft OAuth flow.
        Returns: (provider_user_id, email, name, picture_url)
        """
        # Exchange code for tokens
        token_data = await OAuthService.exchange_microsoft_code(code)
        access_token = token_data["access_token"]
        
        # Get user info
        user_info = await OAuthService.get_microsoft_user_info(access_token)
        
        return (
            user_info["id"],  # Microsoft's unique user ID
            user_info["mail"] or user_info.get("userPrincipalName", "").lower(),
            user_info.get("displayName"),
            None  # Microsoft Graph API requires separate call for photo
        )
