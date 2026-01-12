"""Email service with provider abstraction and Gmail OAuth integration."""
import os
import base64
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.db_models import User, EmailConnection, SentEmail, UserRole


class EmailProvider(ABC):
    """Abstract base class for email providers."""
    
    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_email: Sender email (if applicable)
            attachments: List of attachments (optional)
            
        Returns:
            Dict with message_id and status
        """
        pass


class GmailProvider(EmailProvider):
    """Gmail email provider using OAuth."""
    
    GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    GMAIL_TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        """
        Initialize Gmail provider.
        
        Args:
            access_token: Gmail OAuth access token
            refresh_token: Gmail OAuth refresh token (for token refresh)
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
    
    @staticmethod
    def create_message(to: str, subject: str, body: str, from_email: Optional[str] = None) -> str:
        """
        Create a MIME message for Gmail API.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            from_email: Sender email
            
        Returns:
            Base64url encoded message
        """
        from_line = f"From: {from_email}\r\n" if from_email else ""
        message = (
            f"{from_line}"
            f"To: {to}\r\n"
            f"Subject: {subject}\r\n\r\n"
            f"{body}"
        )
        
        # Encode to base64url
        encoded = base64.urlsafe_b64encode(message.encode('utf-8')).decode('utf-8')
        return encoded
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send email via Gmail API."""
        # Create message
        message = self.create_message(to, subject, body, from_email)
        
        # Send via Gmail API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GMAIL_SEND_URL,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={"raw": message}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email via Gmail: {response.text}"
                )
            
            result = response.json()
            return {
                "message_id": result.get("id"),
                "status": "sent",
                "provider": "gmail"
            }


class SMTPProvider(EmailProvider):
    """SMTP email provider (placeholder for future implementation)."""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        """
        Initialize SMTP provider.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send email via SMTP (placeholder)."""
        # TODO: Implement SMTP sending
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SMTP provider not yet implemented"
        )


class EmailService:
    """Service for managing email operations."""
    
    # Gmail OAuth configuration
    GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "")
    GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "")
    GMAIL_REDIRECT_URI = os.getenv("GMAIL_REDIRECT_URI", "http://localhost:5173/employee/email/callback")
    GMAIL_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GMAIL_TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    @staticmethod
    def check_employee_permission(user: User):
        """Check if user has permission to use email features."""
        if user.role not in [UserRole.EMPLOYEE, UserRole.EMPLOYEE_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email features are only available to employees"
            )
    
    @staticmethod
    def get_gmail_auth_url(state: str, user_email: str) -> str:
        """
        Generate Gmail OAuth authorization URL.
        
        Args:
            state: CSRF state parameter
            user_email: User email for login hint
            
        Returns:
            Authorization URL
        """
        if not EmailService.GMAIL_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gmail OAuth not configured. Please set GMAIL_CLIENT_ID in environment variables."
            )
        
        # Gmail scopes for sending emails
        scopes = [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
        
        params = {
            "client_id": EmailService.GMAIL_CLIENT_ID,
            "redirect_uri": EmailService.GMAIL_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "access_type": "offline",  # Get refresh token
            "prompt": "consent",  # Force consent to get refresh token
            "login_hint": user_email
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{EmailService.GMAIL_AUTH_URL}?{query_string}"
    
    @staticmethod
    async def exchange_gmail_code(code: str) -> Dict[str, Any]:
        """
        Exchange Gmail authorization code for tokens.
        
        Args:
            code: Authorization code from Gmail
            
        Returns:
            Token response from Gmail
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                EmailService.GMAIL_TOKEN_URL,
                data={
                    "client_id": EmailService.GMAIL_CLIENT_ID,
                    "client_secret": EmailService.GMAIL_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": EmailService.GMAIL_REDIRECT_URI
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange Gmail code: {response.text}"
                )
            
            return response.json()
    
    @staticmethod
    async def get_gmail_user_info(access_token: str) -> Dict[str, Any]:
        """Get user info from Gmail."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get Gmail user info: {response.text}"
                )
            
            return response.json()
    
    @staticmethod
    def encrypt_token(token: str) -> str:
        """
        Encrypt a token for storage.
        
        WARNING: This is a placeholder implementation.
        In production, use proper encryption (AES-256) with a key from KMS/secret manager.
        
        Args:
            token: Token to encrypt
            
        Returns:
            Encrypted token (currently just base64 encoded - NOT SECURE)
        """
        # TODO: Implement proper encryption with KMS
        # For now, just base64 encode (THIS IS NOT SECURE IN PRODUCTION)
        return base64.b64encode(token.encode()).decode()
    
    @staticmethod
    def decrypt_token(encrypted_token: str) -> str:
        """
        Decrypt a token from storage.
        
        WARNING: This is a placeholder implementation.
        
        Args:
            encrypted_token: Encrypted token
            
        Returns:
            Decrypted token
        """
        # TODO: Implement proper decryption with KMS
        # For now, just base64 decode
        return base64.b64decode(encrypted_token.encode()).decode()
    
    @staticmethod
    async def connect_gmail(
        db: Session,
        user: User,
        code: str
    ) -> EmailConnection:
        """
        Connect Gmail account for a user.
        
        Args:
            db: Database session
            user: User object
            code: Authorization code from Gmail
            
        Returns:
            EmailConnection object
        """
        # Check permission
        EmailService.check_employee_permission(user)
        
        # Exchange code for tokens
        token_response = await EmailService.exchange_gmail_code(code)
        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in", 3600)
        
        # Get user info
        user_info = await EmailService.get_gmail_user_info(access_token)
        gmail_email = user_info.get("email")
        
        # Check if connection already exists
        existing = db.query(EmailConnection).filter(
            EmailConnection.user_id == user.id,
            EmailConnection.provider == "gmail",
            EmailConnection.provider_email == gmail_email
        ).first()
        
        if existing:
            # Update existing connection
            existing.access_token_encrypted = EmailService.encrypt_token(access_token)
            if refresh_token:
                existing.refresh_token_encrypted = EmailService.encrypt_token(refresh_token)
            existing.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new connection
        from datetime import timedelta
        connection = EmailConnection(
            user_id=user.id,
            provider="gmail",
            provider_email=gmail_email,
            access_token_encrypted=EmailService.encrypt_token(access_token),
            refresh_token_encrypted=EmailService.encrypt_token(refresh_token) if refresh_token else None,
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            is_active=True
        )
        
        db.add(connection)
        db.commit()
        db.refresh(connection)
        
        return connection
    
    @staticmethod
    async def send_email(
        db: Session,
        user: User,
        to: str,
        subject: str,
        body: str,
        matter_id: Optional[str] = None
    ) -> SentEmail:
        """
        Send an email using user's connected email account.
        
        Args:
            db: Database session
            user: User object (must be employee)
            to: Recipient email
            subject: Email subject
            body: Email body
            matter_id: Optional matter ID to associate with
            
        Returns:
            SentEmail object
        """
        # Check permission
        EmailService.check_employee_permission(user)
        
        # Get active email connection
        connection = db.query(EmailConnection).filter(
            EmailConnection.user_id == user.id,
            EmailConnection.is_active == True
        ).first()
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email connection found. Please connect your email account first."
            )
        
        # Decrypt access token
        access_token = EmailService.decrypt_token(connection.access_token_encrypted)
        
        # Create provider
        if connection.provider == "gmail":
            provider = GmailProvider(
                access_token=access_token,
                refresh_token=EmailService.decrypt_token(connection.refresh_token_encrypted) if connection.refresh_token_encrypted else None
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Email provider '{connection.provider}' not supported"
            )
        
        # Send email
        result = await provider.send_email(
            to=to,
            subject=subject,
            body=body,
            from_email=connection.provider_email
        )
        
        # Record sent email
        sent_email = SentEmail(
            connection_id=connection.id,
            matter_id=matter_id,
            to_email=to,
            subject=subject,
            body_preview=body[:500] if body else None,
            provider_message_id=result.get("message_id"),
            meta_data={"status": result.get("status"), "provider": result.get("provider")}
        )
        
        db.add(sent_email)
        db.commit()
        db.refresh(sent_email)
        
        return sent_email
    
    @staticmethod
    def get_sent_emails(
        db: Session,
        user: User,
        matter_id: Optional[str] = None,
        limit: int = 50
    ) -> List[SentEmail]:
        """
        Get sent emails for a user.
        
        Args:
            db: Database session
            user: User object
            matter_id: Optional matter ID to filter by
            limit: Maximum number of emails to return
            
        Returns:
            List of SentEmail objects
        """
        # Check permission
        EmailService.check_employee_permission(user)
        
        # Get user's connections
        connection_ids = db.query(EmailConnection.id).filter(
            EmailConnection.user_id == user.id
        ).all()
        connection_ids = [c[0] for c in connection_ids]
        
        # Build query
        query = db.query(SentEmail).filter(
            SentEmail.connection_id.in_(connection_ids)
        )
        
        if matter_id:
            query = query.filter(SentEmail.matter_id == matter_id)
        
        # Get emails
        emails = query.order_by(SentEmail.sent_at.desc()).limit(limit).all()
        
        return emails


# Singleton instance
_email_service = None


def get_email_service() -> EmailService:
    """Get the singleton email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
