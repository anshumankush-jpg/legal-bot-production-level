"""Authentication service for user management and session handling."""
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.db_models import (
    User, OAuthIdentity, RefreshToken, PasswordReset, 
    AuditLog, UserRole, OAuthProvider, UserProfile, LawyerStatus
)
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, hash_token, create_password_reset_token
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: Optional[str] = None,
        name: Optional[str] = None,
        role: UserRole = UserRole.CLIENT
    ) -> User:
        """Create a new user account."""
        # Normalize email
        email = email.lower().strip()
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password) if password else None,
            name=name,
            role=role,
            is_active=True,
            is_verified=False,
            is_provisioned=False,
            lawyer_status=LawyerStatus.NOT_APPLICABLE
        )
        
        db.add(user)
        db.flush()  # Get user.id without committing
        
        # Create default profile
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created user: {email} (role: {role.value})")
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        email = email.lower().strip()
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not user.password_hash:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def create_user_tokens(
        db: Session,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Create access and refresh tokens for a user.
        Returns: (access_token, refresh_token)
        """
        # Create access token (JWT)
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "role": user.role.value,
                "name": user.name
            }
        )
        
        # Create refresh token (random string)
        refresh_token_str = create_refresh_token()
        
        # Store hashed refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token_str),
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(refresh_token)
        db.commit()
        
        return access_token, refresh_token_str
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token.
        Implements token rotation: old refresh token is invalidated, new one issued.
        Returns: (new_access_token, new_refresh_token)
        """
        token_hash = hash_token(refresh_token)
        
        # Find refresh token
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if expired
        if db_token.expires_at < datetime.utcnow():
            db.delete(db_token)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Get user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Revoke old token (rotation)
        db.delete(db_token)
        
        # Create new tokens
        new_access_token, new_refresh_token = AuthService.create_user_tokens(
            db, user, db_token.user_agent, db_token.ip_address
        )
        
        logger.info(f"Refreshed tokens for user: {user.email}")
        return new_access_token, new_refresh_token
    
    @staticmethod
    def revoke_refresh_token(db: Session, refresh_token: str) -> bool:
        """Revoke a refresh token (logout)."""
        token_hash = hash_token(refresh_token)
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if db_token:
            db.delete(db_token)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_or_create_oauth_user(
        db: Session,
        provider: OAuthProvider,
        provider_user_id: str,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None
    ) -> User:
        """
        Get or create user from OAuth provider.
        Links OAuth identity to existing user if email matches.
        """
        email = email.lower().strip()
        
        # Check if OAuth identity already exists
        oauth_identity = db.query(OAuthIdentity).filter(
            OAuthIdentity.provider == provider,
            OAuthIdentity.provider_user_id == provider_user_id
        ).first()
        
        if oauth_identity:
            # Return existing user
            user = db.query(User).filter(User.id == oauth_identity.user_id).first()
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            db.commit()
            
            return user
        
        # Check if user with this email exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user (no password since OAuth-only)
            user = User(
                email=email,
                password_hash=None,
                name=name,
                role=UserRole.CLIENT,
                is_active=True,
                is_verified=True,  # OAuth emails are pre-verified
                is_provisioned=False,
                lawyer_status=LawyerStatus.NOT_APPLICABLE,
                last_login_at=datetime.utcnow()
            )
            
            db.add(user)
            db.flush()
            
            # Create default profile
            profile = UserProfile(
                user_id=user.id,
                display_name=name,
                avatar_url=picture
            )
            db.add(profile)
            
            logger.info(f"Created new OAuth user: {email} via {provider.value}")
        else:
            # Update last login
            user.last_login_at = datetime.utcnow()
            logger.info(f"Linked OAuth identity to existing user: {email}")
        
        # Create OAuth identity link
        new_identity = OAuthIdentity(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
            picture=picture
        )
        
        db.add(new_identity)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def log_audit(
        db: Session,
        action: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event."""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(log_entry)
        db.commit()
    
    @staticmethod
    def create_password_reset(db: Session, email: str) -> Optional[str]:
        """
        Create a password reset token for user.
        Returns token if user found, None otherwise.
        """
        email = email.lower().strip()
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists
            return None
        
        # Create reset token
        token = create_password_reset_token()
        
        reset = PasswordReset(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        db.add(reset)
        db.commit()
        
        logger.info(f"Created password reset token for: {email}")
        return token
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """Reset password using reset token."""
        token_hash = hash_token(token)
        
        reset = db.query(PasswordReset).filter(
            PasswordReset.token_hash == token_hash
        ).first()
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        if reset.expires_at < datetime.utcnow():
            db.delete(reset)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token expired"
            )
        
        # Update password
        user = db.query(User).filter(User.id == reset.user_id).first()
        user.password_hash = hash_password(new_password)
        
        # Delete reset token
        db.delete(reset)
        
        # Revoke all refresh tokens (force re-login)
        db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
        
        db.commit()
        
        logger.info(f"Password reset successful for user: {user.email}")
        return True
