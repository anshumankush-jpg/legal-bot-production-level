"""OAuth service for Google and Microsoft authentication with PKCE."""
import os
import secrets
import hashlib
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlencode
import httpx
from authlib.integrations.httpx_client import OAuth2Client
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.db_models import User, OAuthIdentity, OAuthProvider, UserRole
from app.services.auth_service import AuthService
from app.services.allowlist_service import AllowlistService
from app.core.config import settings

logger = logging.getLogger(__name__)


class OAuthService:
    """Service for handling OAuth authentication."""
    
    # Static URLs that don't depend on env vars
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    MS_USERINFO_URL = "https://graph.microsoft.com/v1.0/me"
    
    @classmethod
    def get_google_client_id(cls) -> str:
        """Get Google Client ID from settings."""
        return settings.GOOGLE_CLIENT_ID or ""
    
    @classmethod
    def get_google_client_secret(cls) -> str:
        """Get Google Client Secret from settings."""
        return settings.GOOGLE_CLIENT_SECRET or ""
    
    @classmethod
    def get_google_redirect_uri(cls) -> str:
        """Get Google Redirect URI from settings."""
        return settings.GOOGLE_REDIRECT_URI or "http://localhost:4200/auth/callback/google"
    
    @classmethod
    def get_ms_client_id(cls) -> str:
        """Get Microsoft Client ID from settings."""
        return settings.MS_CLIENT_ID or ""
    
    @classmethod
    def get_ms_client_secret(cls) -> str:
        """Get Microsoft Client Secret from settings."""
        return settings.MS_CLIENT_SECRET or ""
    
    @classmethod
    def get_ms_tenant(cls) -> str:
        """Get Microsoft Tenant from settings."""
        return settings.MS_TENANT or "common"
    
    @classmethod
    def get_ms_redirect_uri(cls) -> str:
        """Get Microsoft Redirect URI from settings."""
        return settings.MS_REDIRECT_URI or "http://localhost:4200/auth/callback/microsoft"
    
    @classmethod
    def get_ms_auth_url(cls) -> str:
        """Get Microsoft Auth URL at runtime."""
        return f"https://login.microsoftonline.com/{cls.get_ms_tenant()}/oauth2/v2.0/authorize"
    
    @classmethod
    def get_ms_token_url(cls) -> str:
        """Get Microsoft Token URL at runtime."""
        return f"https://login.microsoftonline.com/{cls.get_ms_tenant()}/oauth2/v2.0/token"
    
    @staticmethod
    def generate_pkce_pair() -> Tuple[str, str]:
        """
        Generate PKCE code verifier and challenge.
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge (SHA-256 hash of verifier, base64url encoded)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    @staticmethod
    def generate_state() -> str:
        """Generate a random state parameter for CSRF protection."""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def get_google_auth_url(cls, state: str, code_challenge: str) -> str:
        """
        Generate Google OAuth authorization URL with PKCE.
        
        Args:
            state: CSRF state parameter
            code_challenge: PKCE code challenge
            
        Returns:
            Authorization URL
        """
        client_id = cls.get_google_client_id()
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID in environment variables."
            )
        
        params = {
            "client_id": client_id,
            "redirect_uri": cls.get_google_redirect_uri(),
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",  # Get refresh token
            "prompt": "consent"  # Force consent to get refresh token
        }
        
        # Use urlencode for proper URL encoding
        query_string = urlencode(params)
        return f"{cls.GOOGLE_AUTH_URL}?{query_string}"
    
    @classmethod
    def get_microsoft_auth_url(cls, state: str, code_challenge: str) -> str:
        """
        Generate Microsoft OAuth authorization URL with PKCE.
        
        Args:
            state: CSRF state parameter
            code_challenge: PKCE code challenge
            
        Returns:
            Authorization URL
        """
        client_id = cls.get_ms_client_id()
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Microsoft OAuth not configured. Please set MS_CLIENT_ID in environment variables."
            )
        
        params = {
            "client_id": client_id,
            "redirect_uri": cls.get_ms_redirect_uri(),
            "response_type": "code",
            "scope": "openid email profile User.Read",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "response_mode": "query"
        }
        
        # Use urlencode for proper URL encoding
        query_string = urlencode(params)
        return f"{cls.get_ms_auth_url()}?{query_string}"
    
    @classmethod
    async def exchange_google_code(
        cls,
        code: str,
        code_verifier: str
    ) -> Dict[str, Any]:
        """
        Exchange Google authorization code for tokens.
        
        Args:
            code: Authorization code from Google
            code_verifier: PKCE code verifier
            
        Returns:
            Token response from Google
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                cls.GOOGLE_TOKEN_URL,
                data={
                    "client_id": cls.get_google_client_id(),
                    "client_secret": cls.get_google_client_secret(),
                    "code": code,
                    "code_verifier": code_verifier,
                    "grant_type": "authorization_code",
                    "redirect_uri": cls.get_google_redirect_uri()
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange Google code: {response.text}"
                )
            
            return response.json()
    
    @classmethod
    async def exchange_microsoft_code(
        cls,
        code: str,
        code_verifier: str
    ) -> Dict[str, Any]:
        """
        Exchange Microsoft authorization code for tokens.
        
        Args:
            code: Authorization code from Microsoft
            code_verifier: PKCE code verifier
            
        Returns:
            Token response from Microsoft
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                cls.get_ms_token_url(),
                data={
                    "client_id": cls.get_ms_client_id(),
                    "client_secret": cls.get_ms_client_secret(),
                    "code": code,
                    "code_verifier": code_verifier,
                    "grant_type": "authorization_code",
                    "redirect_uri": cls.get_ms_redirect_uri()
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange Microsoft code: {response.text}"
                )
            
            return response.json()
    
    @staticmethod
    async def get_google_user_info(access_token: str) -> Dict[str, Any]:
        """
        Get user info from Google.
        
        Args:
            access_token: Google access token
            
        Returns:
            User info dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OAuthService.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get Google user info: {response.text}"
                )
            
            return response.json()
    
    @staticmethod
    async def get_microsoft_user_info(access_token: str) -> Dict[str, Any]:
        """
        Get user info from Microsoft Graph API.
        
        Args:
            access_token: Microsoft access token
            
        Returns:
            User info dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OAuthService.MS_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get Microsoft user info: {response.text}"
                )
            
            return response.json()
    
    @staticmethod
    def get_or_create_oauth_user(
        db: Session,
        provider: OAuthProvider,
        provider_user_id: str,
        email: str,
        name: str,
        role: UserRole = UserRole.CLIENT
    ) -> Optional[User]:
        """
        Get user from OAuth data - LOGIN ONLY (no auto-create).
        
        CRITICAL: This does NOT create new users automatically.
        Users must be in the allowlist (identity_users table) to login.
        
        Args:
            db: Database session
            provider: OAuth provider (GOOGLE or MICROSOFT)
            provider_user_id: User ID from provider
            email: User email
            name: User name
            role: User role (ignored for existing users)
            
        Returns:
            User object if found in allowlist, None if not allowed
        """
        # Check if OAuth identity exists
        oauth_identity = db.query(OAuthIdentity).filter(
            OAuthIdentity.provider == provider,
            OAuthIdentity.provider_user_id == provider_user_id
        ).first()
        
        if oauth_identity:
            # OAuth identity exists, get user
            user = db.query(User).filter(User.id == oauth_identity.user_id).first()
            
            if user and user.is_active:
                # Update last login
                user.last_login_at = datetime.utcnow()
                db.commit()
                logger.info(f"OAuth login successful: {email}")
                return user
            else:
                logger.warning(f"OAuth identity found but user inactive: {email}")
                return None
        
        # Check if user exists in allowlist by email
        allowlist_service = AllowlistService()
        user = allowlist_service.get_user_by_email(db, email)
        
        if not user:
            # USER NOT IN ALLOWLIST - DENY ACCESS
            logger.warning(f"ACCESS DENIED: User not in allowlist - {email}")
            return None
        
        # User exists in allowlist - link OAuth identity
        logger.info(f"Linking OAuth identity for allowlist user: {email}")
        new_oauth_identity = OAuthIdentity(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=email
        )
        db.add(new_oauth_identity)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate_google(
        db: Session,
        code: str,
        code_verifier: str,
        intended_role: UserRole = UserRole.CLIENT
    ) -> Optional[User]:
        """
        Authenticate user with Google OAuth - LOGIN ONLY.
        
        CRITICAL: Does NOT create new users.
        Returns None if user not in allowlist.
        
        Args:
            db: Database session
            code: Authorization code from Google
            code_verifier: PKCE code verifier
            intended_role: Role for new users (ignored - user must exist)
            
        Returns:
            User object if in allowlist, None if access denied
        """
        # Exchange code for tokens
        token_response = await OAuthService.exchange_google_code(code, code_verifier)
        access_token = token_response.get("access_token")
        
        # Get user info
        user_info = await OAuthService.get_google_user_info(access_token)
        
        # Extract user data
        provider_user_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name", email.split("@")[0])
        
        # Get user (LOGIN ONLY - no auto-create)
        user = OAuthService.get_or_create_oauth_user(
            db=db,
            provider=OAuthProvider.GOOGLE,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
            role=intended_role
        )
        
        if not user:
            logger.warning(f"Google OAuth: Access denied for {email}")
        
        return user
    
    @staticmethod
    async def authenticate_microsoft(
        db: Session,
        code: str,
        code_verifier: str,
        intended_role: UserRole = UserRole.CLIENT
    ) -> Optional[User]:
        """
        Authenticate user with Microsoft OAuth - LOGIN ONLY.
        
        CRITICAL: Does NOT create new users.
        Returns None if user not in allowlist.
        
        Args:
            db: Database session
            code: Authorization code from Microsoft
            code_verifier: PKCE code verifier
            intended_role: Role for new users (ignored - user must exist)
            
        Returns:
            User object if in allowlist, None if access denied
        """
        # Exchange code for tokens
        token_response = await OAuthService.exchange_microsoft_code(code, code_verifier)
        access_token = token_response.get("access_token")
        
        # Get user info
        user_info = await OAuthService.get_microsoft_user_info(access_token)
        
        # Extract user data
        provider_user_id = user_info.get("id")
        email = user_info.get("mail") or user_info.get("userPrincipalName")
        name = user_info.get("displayName", email.split("@")[0])
        
        # Get user (LOGIN ONLY - no auto-create)
        user = OAuthService.get_or_create_oauth_user(
            db=db,
            provider=OAuthProvider.MICROSOFT,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
            role=intended_role
        )
        
        if not user:
            logger.warning(f"Microsoft OAuth: Access denied for {email}")
        
        return user


# Singleton instance
_oauth_service = None


def get_oauth_service() -> OAuthService:
    """Get the singleton OAuth service instance."""
    global _oauth_service
    if _oauth_service is None:
        _oauth_service = OAuthService()
    return _oauth_service
