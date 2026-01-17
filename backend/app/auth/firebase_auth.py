"""
Firebase Authentication Integration for LegalAI
Handles Google, Microsoft, and Email/Password authentication
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK not installed. Install with: pip install firebase-admin")


class FirebaseAuthService:
    """Firebase Authentication Service"""
    
    def __init__(self):
        self.initialized = False
        self.db = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase SDK not available")
            return
        
        try:
            # Check if already initialized
            firebase_admin.get_app()
            self.initialized = True
            self.db = firestore.client()
            logger.info("Firebase already initialized")
        except ValueError:
            # Initialize new app
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
                logger.info("Firebase initialized with credentials file")
            else:
                # Skip Firebase if no credentials file - don't try cloud metadata (slow timeout)
                # For local development, Firebase is optional
                logger.info("Firebase credentials not found - Firebase features disabled (this is OK for local dev)")
                self.initialized = False
    
    async def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Decoded token with user info, or None if invalid
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None
        
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'provider': self._get_provider_from_token(decoded_token)
            }
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def _get_provider_from_token(self, decoded_token: Dict) -> str:
        """Extract auth provider from token"""
        firebase_info = decoded_token.get('firebase', {})
        sign_in_provider = firebase_info.get('sign_in_provider', '')
        
        if 'google' in sign_in_provider:
            return 'google'
        elif 'microsoft' in sign_in_provider:
            return 'microsoft'
        elif 'password' in sign_in_provider:
            return 'email'
        else:
            return 'unknown'
    
    async def create_custom_token(self, uid: str, additional_claims: Dict = None) -> Optional[str]:
        """
        Create custom token for user
        
        Args:
            uid: User ID
            additional_claims: Additional claims to include
            
        Returns:
            Custom token string
        """
        if not self.initialized:
            return None
        
        try:
            claims = additional_claims or {}
            token = firebase_auth.create_custom_token(uid, claims)
            return token.decode('utf-8') if isinstance(token, bytes) else token
        except Exception as e:
            logger.error(f"Failed to create custom token: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        if not self.initialized:
            return None
        
        try:
            user = firebase_auth.get_user_by_email(email)
            return {
                'uid': user.uid,
                'email': user.email,
                'email_verified': user.email_verified,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'disabled': user.disabled
            }
        except firebase_auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def update_user(self, uid: str, **kwargs) -> bool:
        """Update user properties"""
        if not self.initialized:
            return False
        
        try:
            firebase_auth.update_user(uid, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False
    
    async def revoke_refresh_tokens(self, uid: str) -> bool:
        """Revoke all refresh tokens for a user (logout)"""
        if not self.initialized:
            return False
        
        try:
            firebase_auth.revoke_refresh_tokens(uid)
            return True
        except Exception as e:
            logger.error(f"Failed to revoke tokens: {e}")
            return False
    
    async def set_custom_user_claims(self, uid: str, claims: Dict) -> bool:
        """
        Set custom claims for a user (for RBAC)
        
        Args:
            uid: User ID
            claims: Dict of claims (e.g., {'role': 'lawyer', 'lawyer_status': 'approved'})
        """
        if not self.initialized:
            return False
        
        try:
            firebase_auth.set_custom_user_claims(uid, claims)
            return True
        except Exception as e:
            logger.error(f"Failed to set custom claims: {e}")
            return False


# Global instance
_firebase_service = None

def get_firebase_auth() -> FirebaseAuthService:
    """Get Firebase Auth service instance"""
    global _firebase_service
    if _firebase_service is None:
        _firebase_service = FirebaseAuthService()
    return _firebase_service
