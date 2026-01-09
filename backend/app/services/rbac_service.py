"""
Role-Based Access Control (RBAC) Service
Manages user roles, permissions, and access control for API endpoints.
"""
import logging
from typing import Dict, List, Optional, Set
from enum import Enum
from datetime import datetime
import jwt
import os

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    PREMIUM = "premium"
    STANDARD = "standard"
    GUEST = "guest"


class Permission(str, Enum):
    """System permissions."""
    # Chat permissions
    CHAT_BASIC = "chat:basic"
    CHAT_ADVANCED = "chat:advanced"
    CHAT_UNLIMITED = "chat:unlimited"
    
    # Document permissions
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_OCR = "document:ocr"
    DOCUMENT_BULK = "document:bulk"
    
    # API permissions
    API_CASE_LOOKUP = "api:case_lookup"
    API_AMENDMENT_GENERATION = "api:amendment_generation"
    API_STATUTE_SEARCH = "api:statute_search"
    API_TRANSLATION = "api:translation"
    
    # History permissions
    HISTORY_VIEW = "history:view"
    HISTORY_SEARCH = "history:search"
    HISTORY_EXPORT = "history:export"
    
    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_ANALYTICS = "admin:analytics"


class RBACService:
    """Service for managing role-based access control."""
    
    # Role to permissions mapping
    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        UserRole.GUEST: {
            Permission.CHAT_BASIC,
            Permission.HISTORY_VIEW,
        },
        UserRole.STANDARD: {
            Permission.CHAT_BASIC,
            Permission.CHAT_ADVANCED,
            Permission.DOCUMENT_UPLOAD,
            Permission.DOCUMENT_OCR,
            Permission.HISTORY_VIEW,
            Permission.HISTORY_SEARCH,
            Permission.API_TRANSLATION,
        },
        UserRole.PREMIUM: {
            Permission.CHAT_BASIC,
            Permission.CHAT_ADVANCED,
            Permission.CHAT_UNLIMITED,
            Permission.DOCUMENT_UPLOAD,
            Permission.DOCUMENT_OCR,
            Permission.DOCUMENT_BULK,
            Permission.API_CASE_LOOKUP,
            Permission.API_AMENDMENT_GENERATION,
            Permission.API_STATUTE_SEARCH,
            Permission.API_TRANSLATION,
            Permission.HISTORY_VIEW,
            Permission.HISTORY_SEARCH,
            Permission.HISTORY_EXPORT,
        },
        UserRole.ADMIN: set(Permission),  # All permissions
    }
    
    # Law category to required permissions mapping
    LAW_CATEGORY_PERMISSIONS: Dict[str, Set[Permission]] = {
        "Constitutional Law": {Permission.CHAT_ADVANCED, Permission.API_CASE_LOOKUP},
        "Criminal Law": {Permission.CHAT_ADVANCED, Permission.API_CASE_LOOKUP, Permission.API_STATUTE_SEARCH},
        "Family Law": {Permission.CHAT_ADVANCED, Permission.API_AMENDMENT_GENERATION},
        "Traffic Law": {Permission.CHAT_BASIC, Permission.API_STATUTE_SEARCH},
        "Business Litigation": {Permission.CHAT_ADVANCED, Permission.API_CASE_LOOKUP, Permission.API_AMENDMENT_GENERATION},
        "Real Estate Law": {Permission.CHAT_ADVANCED, Permission.API_AMENDMENT_GENERATION},
        "Immigration Law": {Permission.CHAT_ADVANCED, Permission.API_CASE_LOOKUP},
        "Employment Law": {Permission.CHAT_ADVANCED, Permission.API_CASE_LOOKUP},
        "Tax Law": {Permission.CHAT_ADVANCED, Permission.API_STATUTE_SEARCH},
        "Wills, Estates, and Trusts": {Permission.CHAT_ADVANCED, Permission.API_AMENDMENT_GENERATION},
        "Health Law": {Permission.CHAT_ADVANCED, Permission.API_STATUTE_SEARCH},
    }
    
    def __init__(self):
        """Initialize RBAC service."""
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        logger.info("RBAC service initialized")
    
    def get_role_permissions(self, role: UserRole) -> Set[Permission]:
        """
        Get all permissions for a given role.
        
        Args:
            role: User role
            
        Returns:
            Set of permissions
        """
        return self.ROLE_PERMISSIONS.get(role, set()).copy()
    
    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: User role
            permission: Permission to check
            
        Returns:
            True if role has permission
        """
        role_permissions = self.ROLE_PERMISSIONS.get(role, set())
        return permission in role_permissions
    
    def has_any_permission(self, role: UserRole, permissions: Set[Permission]) -> bool:
        """
        Check if a role has any of the specified permissions.
        
        Args:
            role: User role
            permissions: Set of permissions to check
            
        Returns:
            True if role has at least one permission
        """
        role_permissions = self.ROLE_PERMISSIONS.get(role, set())
        return bool(role_permissions & permissions)
    
    def has_all_permissions(self, role: UserRole, permissions: Set[Permission]) -> bool:
        """
        Check if a role has all of the specified permissions.
        
        Args:
            role: User role
            permissions: Set of permissions to check
            
        Returns:
            True if role has all permissions
        """
        role_permissions = self.ROLE_PERMISSIONS.get(role, set())
        return permissions.issubset(role_permissions)
    
    def can_access_law_category(self, role: UserRole, law_category: str) -> Dict[str, any]:
        """
        Check if a role can access a specific law category.
        
        Args:
            role: User role
            law_category: Law category name
            
        Returns:
            Dictionary with access status and missing permissions
        """
        required_permissions = self.LAW_CATEGORY_PERMISSIONS.get(law_category, {Permission.CHAT_BASIC})
        role_permissions = self.ROLE_PERMISSIONS.get(role, set())
        
        has_access = required_permissions.issubset(role_permissions)
        missing_permissions = required_permissions - role_permissions
        
        return {
            "has_access": has_access,
            "required_permissions": list(required_permissions),
            "missing_permissions": list(missing_permissions),
            "role": role.value
        }
    
    def can_use_api(self, role: UserRole, api_name: str) -> Dict[str, any]:
        """
        Check if a role can use a specific API.
        
        Args:
            role: User role
            api_name: API name (case_lookup, amendment_generation, etc.)
            
        Returns:
            Dictionary with access status
        """
        api_permission_map = {
            "case_lookup": Permission.API_CASE_LOOKUP,
            "amendment_generation": Permission.API_AMENDMENT_GENERATION,
            "statute_search": Permission.API_STATUTE_SEARCH,
            "translation": Permission.API_TRANSLATION,
        }
        
        required_permission = api_permission_map.get(api_name)
        
        if not required_permission:
            return {
                "has_access": False,
                "error": f"Unknown API: {api_name}"
            }
        
        has_access = self.has_permission(role, required_permission)
        
        return {
            "has_access": has_access,
            "api_name": api_name,
            "required_permission": required_permission.value,
            "role": role.value,
            "upgrade_required": not has_access and role != UserRole.PREMIUM
        }
    
    def generate_token(
        self,
        user_id: str,
        role: UserRole,
        expiration_hours: int = 24
    ) -> str:
        """
        Generate JWT token for user authentication.
        
        Args:
            user_id: User identifier
            role: User role
            expiration_hours: Token expiration in hours
            
        Returns:
            JWT token string
        """
        from datetime import timedelta
        
        payload = {
            "user_id": user_id,
            "role": role.value,
            "permissions": [p.value for p in self.get_role_permissions(role)],
            "exp": datetime.utcnow() + timedelta(hours=expiration_hours),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, any]]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def get_user_role_from_token(self, token: str) -> Optional[UserRole]:
        """
        Extract user role from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            UserRole or None if invalid
        """
        payload = self.verify_token(token)
        if payload:
            role_str = payload.get("role")
            try:
                return UserRole(role_str)
            except ValueError:
                return None
        return None
    
    def get_role_limits(self, role: UserRole) -> Dict[str, any]:
        """
        Get usage limits for a role.
        
        Args:
            role: User role
            
        Returns:
            Dictionary with role limits
        """
        limits = {
            UserRole.GUEST: {
                "daily_messages": 10,
                "document_uploads": 0,
                "api_calls": 0,
                "chat_history_days": 1,
            },
            UserRole.STANDARD: {
                "daily_messages": 100,
                "document_uploads": 5,
                "api_calls": 10,
                "chat_history_days": 30,
            },
            UserRole.PREMIUM: {
                "daily_messages": -1,  # Unlimited
                "document_uploads": -1,  # Unlimited
                "api_calls": -1,  # Unlimited
                "chat_history_days": -1,  # Unlimited
            },
            UserRole.ADMIN: {
                "daily_messages": -1,  # Unlimited
                "document_uploads": -1,  # Unlimited
                "api_calls": -1,  # Unlimited
                "chat_history_days": -1,  # Unlimited
            },
        }
        
        return limits.get(role, limits[UserRole.GUEST])
    
    def get_upgrade_recommendation(self, role: UserRole, requested_feature: str) -> Dict[str, any]:
        """
        Get upgrade recommendation for accessing a feature.
        
        Args:
            role: Current user role
            requested_feature: Feature user wants to access
            
        Returns:
            Dictionary with upgrade recommendation
        """
        if role == UserRole.ADMIN or role == UserRole.PREMIUM:
            return {
                "upgrade_needed": False,
                "current_role": role.value
            }
        
        return {
            "upgrade_needed": True,
            "current_role": role.value,
            "recommended_role": UserRole.PREMIUM.value,
            "benefits": [
                "Unlimited chat messages",
                "Unlimited document uploads with OCR",
                "Access to all legal APIs (case lookup, amendments, statutes)",
                "Advanced search and export features",
                "Priority support",
                "All law categories available"
            ],
            "message": f"Upgrade to Premium to access {requested_feature} and unlock all features!"
        }


# Singleton instance
_rbac_service = None

def get_rbac_service() -> RBACService:
    """Get or create the RBAC service singleton."""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service
