"""Authentication service for password auth, JWT tokens, and session management."""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.db_models import User, RefreshToken, UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TTL_MINUTES = int(os.getenv("JWT_ACCESS_TTL_MIN", "30"))  # 30 minutes default
JWT_REFRESH_TTL_DAYS = int(os.getenv("JWT_REFRESH_TTL_DAYS", "30"))  # 30 days default


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token using SHA-256 for database storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_access_token(user: User) -> str:
        """
        Generate a JWT access token.
        
        Args:
            user: User object
            
        Returns:
            JWT access token string
        """
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TTL_MINUTES)
        
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value if isinstance(user.role, UserRole) else user.role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def generate_refresh_token() -> str:
        """Generate a random refresh token."""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def create_refresh_token(
        db: Session,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, RefreshToken]:
        """
        Create and store a refresh token.
        
        Args:
            db: Database session
            user: User object
            user_agent: User agent string
            ip_address: IP address
            
        Returns:
            Tuple of (token_string, RefreshToken object)
        """
        token_string = AuthService.generate_refresh_token()
        token_hash = AuthService.hash_token(token_string)
        
        expires_at = datetime.utcnow() + timedelta(days=JWT_REFRESH_TTL_DAYS)
        
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        
        return token_string, refresh_token
    
    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT access token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Check token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    @staticmethod
    def verify_refresh_token(
        db: Session,
        token_string: str
    ) -> Optional[RefreshToken]:
        """
        Verify a refresh token and return the token object if valid.
        
        Args:
            db: Database session
            token_string: Refresh token string
            
        Returns:
            RefreshToken object if valid, None otherwise
        """
        token_hash = AuthService.hash_token(token_string)
        
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if not refresh_token:
            return None
        
        # Check if token is valid
        if not refresh_token.is_valid:
            return None
        
        return refresh_token
    
    @staticmethod
    def rotate_refresh_token(
        db: Session,
        old_token: RefreshToken,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, RefreshToken]:
        """
        Rotate a refresh token (revoke old, create new).
        
        Args:
            db: Database session
            old_token: Old RefreshToken object
            user_agent: User agent string
            ip_address: IP address
            
        Returns:
            Tuple of (new_token_string, new RefreshToken object)
        """
        # Revoke old token
        old_token.revoked_at = datetime.utcnow()
        
        # Create new token
        user = db.query(User).filter(User.id == old_token.user_id).first()
        new_token_string, new_token_obj = AuthService.create_refresh_token(
            db, user, user_agent, ip_address
        )
        
        # Link tokens for audit trail
        old_token.replaced_by_token_id = new_token_obj.id
        
        db.commit()
        
        return new_token_string, new_token_obj
    
    @staticmethod
    def revoke_refresh_token(db: Session, token: RefreshToken):
        """Revoke a refresh token."""
        token.revoked_at = datetime.utcnow()
        db.commit()
    
    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: str):
        """Revoke all refresh tokens for a user (e.g., on password change)."""
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        ).all()
        
        for token in tokens:
            token.revoked_at = datetime.utcnow()
        
        db.commit()
    
    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        name: str,
        role: UserRole = UserRole.CLIENT
    ) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            name: User name
            role: User role
            
        Returns:
            Created User object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            role=role,
            is_active=True,
            is_verified=False  # Email verification can be added later
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not user.password_hash:
            # OAuth-only user, no password set
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def change_password(
        db: Session,
        user: User,
        old_password: str,
        new_password: str
    ):
        """
        Change user password.
        
        Args:
            db: Database session
            user: User object
            old_password: Current password
            new_password: New password
            
        Raises:
            HTTPException: If old password is incorrect
        """
        if not user.password_hash or not AuthService.verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        
        user.password_hash = AuthService.hash_password(new_password)
        db.commit()
        
        # Revoke all refresh tokens for security
        AuthService.revoke_all_user_tokens(db, user.id)


# Singleton instance
_auth_service = None


def get_auth_service() -> AuthService:
    """Get the singleton auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
