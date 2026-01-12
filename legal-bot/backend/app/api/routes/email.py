"""Email API routes for employee portal."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User, AuditLog
from app.api.routes.auth import get_current_user
from app.services.email_service import get_email_service, EmailService

router = APIRouter(prefix="/api/email", tags=["email"])


# Request/Response Models

class EmailConnectStartResponse(BaseModel):
    auth_url: str
    state: str
    provider: str


class EmailConnectExchangeRequest(BaseModel):
    code: str
    state: str


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    matter_id: Optional[str] = None


class SentEmailResponse(BaseModel):
    id: str
    to_email: str
    subject: str
    body_preview: Optional[str]
    sent_at: str
    matter_id: Optional[str]
    provider_message_id: Optional[str]


class EmailConnectionResponse(BaseModel):
    id: str
    provider: str
    provider_email: str
    is_active: bool
    created_at: str


# Helper Functions

def log_audit(db: Session, user_id: str, action_type: str, details: dict):
    """Log an audit event."""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            action_details=details
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Failed to log audit: {e}")


# Email Connection Endpoints

@router.get("/connect/gmail/start", response_model=EmailConnectStartResponse)
async def start_gmail_connection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start Gmail OAuth connection flow.
    Returns authorization URL for user to visit.
    """
    email_service = get_email_service()
    
    # Check permission
    email_service.check_employee_permission(current_user)
    
    # Generate state
    import secrets
    state = secrets.token_urlsafe(32)
    
    # Get authorization URL
    auth_url = email_service.get_gmail_auth_url(state, current_user.email)
    
    # Log audit
    log_audit(db, current_user.id, "EMAIL_CONNECT_STARTED", {"provider": "gmail"})
    
    return {
        "auth_url": auth_url,
        "state": state,
        "provider": "gmail"
    }


@router.post("/connect/gmail/exchange")
async def exchange_gmail_code(
    request_data: EmailConnectExchangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exchange Gmail authorization code for tokens and create email connection.
    """
    email_service = get_email_service()
    
    # Connect Gmail
    connection = await email_service.connect_gmail(
        db=db,
        user=current_user,
        code=request_data.code
    )
    
    # Log audit
    log_audit(db, current_user.id, "EMAIL_CONNECT_COMPLETED", {
        "provider": "gmail",
        "provider_email": connection.provider_email
    })
    
    return {
        "message": "Gmail connected successfully",
        "connection": {
            "id": connection.id,
            "provider": connection.provider,
            "provider_email": connection.provider_email,
            "is_active": connection.is_active
        }
    }


@router.get("/connections", response_model=List[EmailConnectionResponse])
async def get_email_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all email connections for current user."""
    email_service = get_email_service()
    email_service.check_employee_permission(current_user)
    
    from app.models.db_models import EmailConnection
    connections = db.query(EmailConnection).filter(
        EmailConnection.user_id == current_user.id
    ).all()
    
    return [
        EmailConnectionResponse(
            id=conn.id,
            provider=conn.provider,
            provider_email=conn.provider_email,
            is_active=conn.is_active,
            created_at=conn.created_at.isoformat()
        )
        for conn in connections
    ]


# Email Sending Endpoints

@router.post("/send")
async def send_email(
    request_data: SendEmailRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send an email using connected email account.
    """
    email_service = get_email_service()
    
    # Send email
    sent_email = await email_service.send_email(
        db=db,
        user=current_user,
        to=request_data.to,
        subject=request_data.subject,
        body=request_data.body,
        matter_id=request_data.matter_id
    )
    
    # Log audit
    log_audit(db, current_user.id, "EMAIL_SENT", {
        "to": request_data.to,
        "subject": request_data.subject,
        "matter_id": request_data.matter_id
    })
    
    return {
        "message": "Email sent successfully",
        "email_id": sent_email.id,
        "sent_at": sent_email.sent_at.isoformat()
    }


@router.get("/sent", response_model=List[SentEmailResponse])
async def get_sent_emails(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    matter_id: Optional[str] = None,
    limit: int = 50
):
    """Get sent emails for current user."""
    email_service = get_email_service()
    
    emails = email_service.get_sent_emails(
        db=db,
        user=current_user,
        matter_id=matter_id,
        limit=limit
    )
    
    return [
        SentEmailResponse(
            id=email.id,
            to_email=email.to_email,
            subject=email.subject,
            body_preview=email.body_preview,
            sent_at=email.sent_at.isoformat(),
            matter_id=email.matter_id,
            provider_message_id=email.provider_message_id
        )
        for email in emails
    ]


@router.get("/draft")
async def get_email_draft_template(
    matter_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a draft email template (optional feature).
    Can be enhanced to generate AI-powered email drafts based on matter context.
    """
    email_service = get_email_service()
    email_service.check_employee_permission(current_user)
    
    # Basic template
    template = {
        "subject": "",
        "body": "Dear [Recipient],\n\n\n\nBest regards,\n[Your Name]",
        "matter_id": matter_id
    }
    
    # If matter_id provided, could enhance with matter context
    if matter_id:
        from app.models.db_models import MatterDB
        matter = db.query(MatterDB).filter(MatterDB.id == matter_id).first()
        if matter:
            template["subject"] = f"Regarding: {matter.title}"
    
    return template
