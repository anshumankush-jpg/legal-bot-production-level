"""
Upload Routes for LegalAI
Handles file uploads with user scoping (ChatGPT-like attachments)
"""
import uuid
import hashlib
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.middleware.auth_middleware import get_current_user
from app.services.storage_service import get_storage_service, StorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SignedUrlRequest(BaseModel):
    """Request for signed upload URL"""
    fileName: str = Field(..., min_length=1, max_length=255)
    fileType: str = Field(..., description="MIME type (e.g., image/png, application/pdf)")
    fileSize: int = Field(..., gt=0, le=10*1024*1024, description="File size in bytes (max 10MB)")
    conversation_id: Optional[str] = Field(None, description="Optional conversation to attach to")


class SignedUrlResponse(BaseModel):
    """Signed URL for direct GCS upload"""
    attachment_id: str
    signedUrl: str
    gcsUrl: str
    expiresAt: datetime


class ConfirmUploadRequest(BaseModel):
    """Confirm upload completion"""
    conversation_id: Optional[str] = None
    sha256: Optional[str] = None


class AttachmentResponse(BaseModel):
    """Attachment metadata"""
    attachment_id: str
    user_id: str
    conversation_id: Optional[str]
    file_name: str
    file_type: str
    file_size: int
    gcs_url: str
    sha256: Optional[str]
    uploaded_at: datetime
    metadata: Optional[dict]


# Allowed file types (strict security)
ALLOWED_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/gif',
    'image/webp',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ============================================================================
# UPLOAD ROUTES
# ============================================================================

@router.post("/signed-url", response_model=SignedUrlResponse)
async def get_signed_upload_url(
    req: SignedUrlRequest,
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Get signed URL for direct file upload to GCS.
    
    SECURITY:
    - Validates file type and size
    - Creates user-scoped path in GCS
    - Returns short-lived signed URL (15 min)
    
    ChatGPT behavior: User uploads → GCS → confirm → attach to conversation
    """
    # Validate file type
    if req.fileType not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed: {req.fileType}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Validate file size
    if req.fileSize > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large: {req.fileSize} bytes. Max allowed: {MAX_FILE_SIZE} bytes (10MB)"
        )
    
    # Generate attachment ID
    attachment_id = str(uuid.uuid4())
    
    # Create user-scoped GCS path
    # Pattern: attachments/{user_id}/{attachment_id}/{filename}
    gcs_path = f"attachments/{user['user_id']}/{attachment_id}/{req.fileName}"
    
    # Generate signed URL
    signed_url_data = await storage.generate_signed_upload_url(
        path=gcs_path,
        content_type=req.fileType,
        expires_minutes=15
    )
    
    if not signed_url_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate signed URL"
        )
    
    # Save attachment metadata (status: uploading)
    await storage.create_attachment_metadata(
        attachment_id=attachment_id,
        user_id=user['user_id'],
        conversation_id=req.conversation_id,
        file_name=req.fileName,
        file_type=req.fileType,
        file_size=req.fileSize,
        gcs_url=signed_url_data['gcs_url'],
        status='uploading'
    )
    
    return SignedUrlResponse(
        attachment_id=attachment_id,
        signedUrl=signed_url_data['signed_url'],
        gcsUrl=signed_url_data['gcs_url'],
        expiresAt=signed_url_data['expires_at']
    )


@router.post("/{attachment_id}/confirm", response_model=AttachmentResponse)
async def confirm_upload(
    attachment_id: str,
    confirm_req: ConfirmUploadRequest,
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Confirm upload completion and process file.
    
    SECURITY: Verifies attachment belongs to user_id from session.
    
    Steps:
    1. Verify file exists in GCS
    2. Update attachment status to 'completed'
    3. Optionally run OCR/virus scan
    4. Return attachment metadata
    """
    # Verify ownership and update
    attachment = await storage.confirm_upload(
        attachment_id=attachment_id,
        user_id=user['user_id'],
        conversation_id=confirm_req.conversation_id,
        sha256=confirm_req.sha256
    )
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found or access denied"
        )
    
    return attachment


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: str,
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Get attachment metadata.
    
    SECURITY: user_id scoping.
    """
    attachment = await storage.get_attachment(
        attachment_id=attachment_id,
        user_id=user['user_id']
    )
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found or access denied"
        )
    
    return attachment


@router.get("/conversation/{conversation_id}/attachments", response_model=list[AttachmentResponse])
async def list_conversation_attachments(
    conversation_id: str,
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service)
):
    """
    List attachments for conversation.
    
    SECURITY: user_id scoping.
    ChatGPT behavior: Show uploaded files in conversation context.
    """
    attachments = await storage.list_attachments(
        conversation_id=conversation_id,
        user_id=user['user_id']
    )
    
    return attachments
