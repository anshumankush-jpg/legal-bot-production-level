"""
Allowlist service - LOGIN ONLY (no auto-signup).
Users must be pre-approved to access the app.
"""
import logging
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.db_models import User

logger = logging.getLogger(__name__)


class AllowlistService:
    """
    Service for checking if users are allowed to access the app.
    
    CRITICAL SECURITY RULE:
    - Users must exist in our database to login
    - We do NOT auto-create accounts on first OAuth login
    - Only pre-approved users (is_allowed=True) can access
    """
    
    @staticmethod
    def is_user_allowed(db: Session, email: str, auth_provider: str = None) -> bool:
        """
        Check if user is in allowlist.
        
        Args:
            db: Database session
            email: User email
            auth_provider: Optional provider filter
            
        Returns:
            True if user exists and is allowed, False otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"Access denied: User not in allowlist - {email}")
            return False
        
        if not user.is_active:
            logger.warning(f"Access denied: User account inactive - {email}")
            return False
        
        logger.info(f"Access allowed: User in allowlist - {email}")
        return True
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email if they exist in allowlist.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object if found and allowed, None otherwise
        """
        user = db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()
        
        return user
    
    @staticmethod
    def check_profile_completed(db: Session, user_id: str) -> bool:
        """
        Check if user has completed their profile setup.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if profile is complete, False otherwise
        """
        # Check if user has profile data
        # For now, check if user has name and other required fields
        # Later, this will check a separate user_profiles table
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        # Check required profile fields
        if not user.name or user.name.strip() == "":
            return False
        
        # Add more checks as needed (address, phone, etc.)
        # For now, just check if name is set
        
        return True
    
    @staticmethod
    def create_allowlist_user(
        db: Session,
        email: str,
        name: str,
        role: str = "customer",
        auth_provider: str = "email"
    ) -> User:
        """
        Admin function to add a user to the allowlist.
        This should only be called by admin tools, not during login.
        
        Args:
            db: Database session
            email: User email
            name: User name
            role: User role (customer|lawyer|admin)
            auth_provider: Auth provider
            
        Returns:
            Created user
        """
        from app.models.db_models import UserRole
        
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            logger.info(f"User already in allowlist: {email}")
            return existing
        
        # Create new user
        user = User(
            email=email,
            name=name,
            role=UserRole(role),
            is_active=True,
            is_verified=False  # Will be verified after profile setup
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Added user to allowlist: {email}")
        return user


# Singleton
_allowlist_service = None


def get_allowlist_service() -> AllowlistService:
    """Get allowlist service singleton."""
    global _allowlist_service
    if _allowlist_service is None:
        _allowlist_service = AllowlistService()
    return _allowlist_service
