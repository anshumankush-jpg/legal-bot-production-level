"""Password reset service for forgot password flow."""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.db_models import User, PasswordReset
from app.services.auth_service import AuthService


class PasswordResetService:
    """Service for handling password reset operations."""
    
    RESET_TOKEN_TTL_MINUTES = 30  # 30 minutes validity
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a random password reset token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token using SHA-256."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def create_reset_token(
        db: Session,
        user: User
    ) -> str:
        """
        Create a password reset token.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Reset token string
        """
        # Invalidate any existing unused tokens for this user
        existing_tokens = db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.used_at.is_(None)
        ).all()
        
        for token in existing_tokens:
            token.used_at = datetime.utcnow()  # Mark as used to invalidate
        
        # Generate new token
        token_string = PasswordResetService.generate_reset_token()
        token_hash = PasswordResetService.hash_token(token_string)
        
        expires_at = datetime.utcnow() + timedelta(
            minutes=PasswordResetService.RESET_TOKEN_TTL_MINUTES
        )
        
        reset_token = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        db.add(reset_token)
        db.commit()
        
        return token_string
    
    @staticmethod
    def verify_reset_token(
        db: Session,
        token_string: str
    ) -> Optional[PasswordReset]:
        """
        Verify a password reset token.
        
        Args:
            db: Database session
            token_string: Reset token string
            
        Returns:
            PasswordReset object if valid, None otherwise
        """
        token_hash = PasswordResetService.hash_token(token_string)
        
        reset_token = db.query(PasswordReset).filter(
            PasswordReset.token_hash == token_hash
        ).first()
        
        if not reset_token:
            return None
        
        # Check if token is valid
        if not reset_token.is_valid:
            return None
        
        return reset_token
    
    @staticmethod
    def reset_password(
        db: Session,
        token_string: str,
        new_password: str
    ):
        """
        Reset user password using a reset token.
        
        Args:
            db: Database session
            token_string: Reset token string
            new_password: New password (plain text)
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        # Verify token
        reset_token = PasswordResetService.verify_reset_token(db, token_string)
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.password_hash = AuthService.hash_password(new_password)
        
        # Mark token as used
        reset_token.used_at = datetime.utcnow()
        
        db.commit()
        
        # Revoke all refresh tokens for security
        AuthService.revoke_all_user_tokens(db, user.id)
    
    @staticmethod
    def send_reset_email(email: str, reset_token: str):
        """
        Send password reset email.
        
        For now, this is a stub that logs the reset link.
        In production, integrate with email provider (SendGrid, AWS SES, etc.)
        
        Args:
            email: User email
            reset_token: Reset token to include in email
        """
        # Build reset link
        frontend_url = "http://localhost:5173"  # TODO: Get from environment
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        # TODO: Implement actual email sending
        # For now, log to console for development
        print("\n" + "="*80)
        print("PASSWORD RESET EMAIL")
        print("="*80)
        print(f"To: {email}")
        print(f"Reset Link: {reset_link}")
        print("="*80 + "\n")
        
        # In production, use email provider:
        # email_provider.send_email(
        #     to=email,
        #     subject="Reset Your Password",
        #     body=f"Click here to reset your password: {reset_link}"
        # )


# Singleton instance
_password_reset_service = None


def get_password_reset_service() -> PasswordResetService:
    """Get the singleton password reset service instance."""
    global _password_reset_service
    if _password_reset_service is None:
        _password_reset_service = PasswordResetService()
    return _password_reset_service
