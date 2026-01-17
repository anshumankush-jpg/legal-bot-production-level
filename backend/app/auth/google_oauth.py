"""Google OAuth 2.0 authentication handler."""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GoogleUserInfo(BaseModel):
    """Google user information model."""
    sub: str  # Google user ID
    email: str
    email_verified: bool
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None


class GoogleOAuthHandler:
    """Handles Google OAuth 2.0 authentication flow."""
    
    def __init__(self):
        """Initialize Google OAuth handler with credentials from environment."""
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))
        
        # Google OAuth endpoints
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        
        # Validate configuration
        if not self.client_id or not self.client_secret:
            logger.error("Google OAuth credentials not configured in environment variables")
            raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment variables")
        
        logger.info(f"Google OAuth initialized with redirect URI: {self.redirect_uri}")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",  # Get refresh token
            "prompt": "consent",  # Force consent screen to get refresh token
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{self.auth_url}?{query_string}"
        
        logger.info(f"Generated authorization URL with state: {state}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Token response containing access_token, refresh_token, etc.
        """
        logger.info("Exchanging authorization code for access token")
        
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                
                logger.info("Successfully exchanged code for token")
                return token_data
        except httpx.HTTPError as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> GoogleUserInfo:
        """
        Get user information from Google using access token.
        
        Args:
            access_token: Google access token
            
        Returns:
            User information from Google
        """
        logger.info("Fetching user info from Google")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.userinfo_url, headers=headers)
                response.raise_for_status()
                user_data = response.json()
                
                user_info = GoogleUserInfo(**user_data)
                logger.info(f"Successfully fetched user info for: {user_info.email}")
                return user_info
        except httpx.HTTPError as e:
            logger.error(f"Error fetching user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch user information: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error parsing user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse user information: {str(e)}"
            )
    
    def create_jwt_token(self, user_info: GoogleUserInfo) -> str:
        """
        Create JWT token for authenticated user.
        
        Args:
            user_info: Google user information
            
        Returns:
            JWT token string
        """
        logger.info(f"Creating JWT token for user: {user_info.email}")
        
        payload = {
            "sub": user_info.sub,  # Google user ID
            "email": user_info.email,
            "name": user_info.name,
            "picture": user_info.picture,
            "email_verified": user_info.email_verified,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=self.jwt_expiration),
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        logger.info(f"JWT token created successfully for {user_info.email}")
        return token
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            logger.info(f"JWT token verified for user: {payload.get('email')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


# Singleton instance
_google_oauth_handler: Optional[GoogleOAuthHandler] = None


def get_google_oauth_handler() -> GoogleOAuthHandler:
    """Get or create singleton GoogleOAuthHandler instance."""
    global _google_oauth_handler
    if _google_oauth_handler is None:
        _google_oauth_handler = GoogleOAuthHandler()
    return _google_oauth_handler
