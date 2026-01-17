"""
Authentication Middleware for LegalAI
Handles token verification and role-based access control
"""
import logging
from typing import Optional, Dict, List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.firebase_auth import get_firebase_auth, FirebaseAuthService
from app.auth.bigquery_client import get_bigquery_client, BigQueryIdentityClient

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class AuthMiddleware:
    """Authentication and authorization middleware"""
    
    def __init__(self):
        self.firebase = get_firebase_auth()
        self.bq_client = get_bigquery_client()
    
    async def verify_token(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """
        Verify Firebase ID token and return user info
        
        Raises:
            HTTPException: If token is invalid
        """
        token = credentials.credentials
        
        # Verify with Firebase
        user_data = await self.firebase.verify_token(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get full user profile from BigQuery
        user_id = await self.bq_client.get_user_id(
            user_data['uid'],
            user_data['provider']
        )
        
        if user_id:
            user_profile = await self.bq_client.get_user_by_id(user_id)
            if user_profile:
                user_data.update(user_profile)
        
        return user_data
    
    async def require_role(
        self,
        required_role: str,
        user: Dict = Depends(verify_token)
    ) -> Dict:
        """
        Require specific role
        
        Args:
            required_role: Role name (customer|lawyer|admin)
            user: Current user from verify_token
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        if user.get('role') != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        
        return user
    
    async def require_verified_lawyer(
        self,
        user: Dict = Depends(verify_token)
    ) -> Dict:
        """
        Require verified lawyer status
        
        Raises:
            HTTPException: If user is not a verified lawyer
        """
        if user.get('role') != 'lawyer':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Lawyer role required."
            )
        
        if user.get('lawyer_status') != 'approved':
            status_msg = {
                'pending': "Your lawyer application is pending review.",
                'rejected': "Your lawyer application was rejected.",
                None: "Please submit a lawyer application."
            }.get(user.get('lawyer_status'), "Verification required.")
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=status_msg
            )
        
        return user
    
    async def require_admin(
        self,
        user: Dict = Depends(verify_token)
    ) -> Dict:
        """
        Require admin role
        
        Raises:
            HTTPException: If user is not an admin
        """
        if user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Admin role required."
            )
        
        return user


# Global instance
_auth_middleware = AuthMiddleware()


# Dependency functions (use these in route parameters)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Get current authenticated user"""
    return await _auth_middleware.verify_token(credentials)


async def get_current_customer(
    user: Dict = Depends(get_current_user)
) -> Dict:
    """Get current user if customer"""
    return await _auth_middleware.require_role('customer', user)


async def get_current_lawyer(
    user: Dict = Depends(get_current_user)
) -> Dict:
    """Get current user if lawyer (any status)"""
    return await _auth_middleware.require_role('lawyer', user)


async def get_verified_lawyer(
    user: Dict = Depends(get_current_user)
) -> Dict:
    """Get current user if verified lawyer"""
    return await _auth_middleware.require_verified_lawyer(user)


async def get_current_admin(
    user: Dict = Depends(get_current_user)
) -> Dict:
    """Get current user if admin"""
    return await _auth_middleware.require_admin(user)


# Optional: allow unauthenticated but inject user if present
async def get_optional_user(
    request: Request
) -> Optional[Dict]:
    """Get user if authenticated, None otherwise"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.replace('Bearer ', '')
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        return await _auth_middleware.verify_token(credentials)
    except Exception:
        return None
