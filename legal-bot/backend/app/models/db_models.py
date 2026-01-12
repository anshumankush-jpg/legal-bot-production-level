"""Database models for authentication and authorization."""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import (
    Column, String, DateTime, Boolean, Enum as SQLEnum,
    ForeignKey, Text, Integer, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from enum import Enum

from app.database import Base


class UserRole(str, Enum):
    """User roles with different permission levels."""
    CLIENT = "client"
    LAWYER = "lawyer"
    EMPLOYEE = "employee"
    EMPLOYEE_ADMIN = "employee_admin"


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users
    name = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CLIENT)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Metadata
    profile_data = Column(JSON, default=dict)  # Additional profile info
    
    # Relationships
    oauth_identities = relationship("OAuthIdentity", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    employee_assignments = relationship("EmployeeAssignment", 
                                       foreign_keys="[EmployeeAssignment.employee_user_id]",
                                       back_populates="employee")
    matters = relationship("MatterDB", back_populates="user")
    email_connections = relationship("EmailConnection", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class OAuthIdentity(Base):
    """OAuth identity linking for users."""
    __tablename__ = "oauth_identities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider = Column(SQLEnum(OAuthProvider), nullable=False)
    provider_user_id = Column(String(255), nullable=False)  # sub/id from OAuth provider
    provider_email = Column(String(255), nullable=True)
    
    access_token_encrypted = Column(Text, nullable=True)  # Encrypted, if storing
    refresh_token_encrypted = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="oauth_identities")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uix_provider_user'),
        Index('idx_oauth_provider_email', 'provider', 'provider_email'),
    )

    def __repr__(self):
        return f"<OAuthIdentity {self.provider}:{self.provider_user_id}>"


class RefreshToken(Base):
    """Refresh tokens for JWT authentication."""
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by_token_id = Column(String(36), nullable=True)  # For token rotation
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # User agent / IP for security
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return (
            self.revoked_at is None and
            self.expires_at > datetime.utcnow()
        )

    def __repr__(self):
        return f"<RefreshToken {self.id} for user {self.user_id}>"


class PasswordReset(Base):
    """Password reset tokens."""
    __tablename__ = "password_resets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="password_resets")

    @property
    def is_valid(self) -> bool:
        """Check if reset token is still valid."""
        return (
            self.used_at is None and
            self.expires_at > datetime.utcnow()
        )

    def __repr__(self):
        return f"<PasswordReset {self.id} for user {self.user_id}>"


class MatterDB(Base):
    """Legal matter/case in database."""
    __tablename__ = "matters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    matter_type = Column(String(100), nullable=True)  # traffic_ticket, contract, etc.
    status = Column(String(50), default="active", nullable=False)
    
    jurisdiction_data = Column(JSON, default=dict)  # {country, region, region_code}
    structured_data = Column(JSON, default=dict)  # Parsed data from documents
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="matters")
    messages = relationship("Message", back_populates="matter", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="matter", cascade="all, delete-orphan")
    share_packages = relationship("SharePackage", back_populates="matter", cascade="all, delete-orphan")
    employee_assignments = relationship("EmployeeAssignment", back_populates="matter", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_matters_user_status', 'user_id', 'status'),
    )

    def __repr__(self):
        return f"<MatterDB {self.title} ({self.status})>"


class Message(Base):
    """Chat messages for a matter."""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    matter_id = Column(String(36), ForeignKey("matters.id"), nullable=False)
    
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    meta_data = Column(JSON, default=dict)
    
    # Relationships
    matter = relationship("MatterDB", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_messages_matter_created', 'matter_id', 'created_at'),
    )

    def __repr__(self):
        return f"<Message {self.role} in matter {self.matter_id}>"


class Document(Base):
    """Documents uploaded or generated for a matter."""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    matter_id = Column(String(36), ForeignKey("matters.id"), nullable=False)
    
    filename = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    storage_path = Column(String(1000), nullable=True)  # Local or cloud path
    
    document_type = Column(String(100), nullable=True)  # uploaded, generated, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    meta_data = Column(JSON, default=dict)
    
    # Relationships
    matter = relationship("MatterDB", back_populates="documents")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_matter', 'matter_id'),
    )

    def __repr__(self):
        return f"<Document {self.filename} in matter {self.matter_id}>"


class SharePackage(Base):
    """Share package for sharing matter data with lawyers."""
    __tablename__ = "share_packages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    matter_id = Column(String(36), ForeignKey("matters.id"), nullable=False)
    shared_with_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # If shared with specific user
    
    share_token = Column(String(255), unique=True, index=True, nullable=False)
    
    include_messages = Column(Boolean, default=True)
    include_documents = Column(Boolean, default=True)
    include_summary = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    accessed_at = Column(DateTime, nullable=True)
    
    # Relationships
    matter = relationship("MatterDB", back_populates="share_packages")
    
    @property
    def is_active(self) -> bool:
        """Check if share package is still active."""
        if self.revoked_at is not None:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

    def __repr__(self):
        return f"<SharePackage {self.share_token[:8]}... for matter {self.matter_id}>"


class EmployeeAssignment(Base):
    """Employee assignments to matters for scoped access."""
    __tablename__ = "employee_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    matter_id = Column(String(36), ForeignKey("matters.id"), nullable=False)
    
    assigned_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("User", foreign_keys=[employee_user_id], back_populates="employee_assignments")
    matter = relationship("MatterDB", back_populates="employee_assignments")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('employee_user_id', 'matter_id', name='uix_employee_matter'),
        Index('idx_assignments_employee', 'employee_user_id'),
        Index('idx_assignments_matter', 'matter_id'),
    )

    @property
    def is_active(self) -> bool:
        """Check if assignment is still active."""
        return self.revoked_at is None

    def __repr__(self):
        return f"<EmployeeAssignment employee:{self.employee_user_id} matter:{self.matter_id}>"


class AuditLog(Base):
    """Audit log for tracking sensitive actions."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    action_type = Column(String(100), nullable=False)  # AUTH_LOGIN, MATTER_VIEWED, EMAIL_SENT, etc.
    action_details = Column(JSON, default=dict)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_action_created', 'action_type', 'created_at'),
        Index('idx_audit_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f"<AuditLog {self.action_type} by user {self.user_id}>"


class EmailConnection(Base):
    """Email provider connections for employees (Gmail OAuth, etc.)."""
    __tablename__ = "email_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    provider = Column(String(50), nullable=False)  # gmail, outlook, etc.
    provider_email = Column(String(255), nullable=False)
    
    access_token_encrypted = Column(Text, nullable=True)  # Encrypted
    refresh_token_encrypted = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="email_connections")
    sent_emails = relationship("SentEmail", back_populates="connection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EmailConnection {self.provider}:{self.provider_email} for user {self.user_id}>"


class SentEmail(Base):
    """Record of sent emails for audit trail."""
    __tablename__ = "sent_emails"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    connection_id = Column(String(36), ForeignKey("email_connections.id"), nullable=False)
    matter_id = Column(String(36), ForeignKey("matters.id"), nullable=True)
    
    to_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body_preview = Column(Text, nullable=True)  # First 500 chars
    
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    provider_message_id = Column(String(500), nullable=True)
    
    meta_data = Column(JSON, default=dict)
    
    # Relationships
    connection = relationship("EmailConnection", back_populates="sent_emails")
    
    # Indexes
    __table_args__ = (
        Index('idx_sent_emails_matter', 'matter_id'),
        Index('idx_sent_emails_sent_at', 'sent_at'),
    )

    def __repr__(self):
        return f"<SentEmail to:{self.to_email} at {self.sent_at}>"


class BookingRequest(Base):
    """Lawyer booking requests from clients."""
    __tablename__ = "booking_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    matter_id = Column(String(36), ForeignKey("matters.id"), nullable=True)
    client_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    lawyer_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    status = Column(String(50), default="pending", nullable=False)  # pending, accepted, rejected, completed
    
    requested_date = Column(DateTime, nullable=True)
    confirmed_date = Column(DateTime, nullable=True)
    
    client_notes = Column(Text, nullable=True)
    lawyer_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_bookings_client', 'client_user_id'),
        Index('idx_bookings_lawyer', 'lawyer_user_id'),
        Index('idx_bookings_status', 'status'),
    )

    def __repr__(self):
        return f"<BookingRequest {self.status} for client {self.client_user_id}>"


class LawyerProfile(Base):
    """Extended profile for lawyer users."""
    __tablename__ = "lawyer_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    
    bar_number = Column(String(100), nullable=True)
    firm_name = Column(String(500), nullable=True)
    specializations = Column(JSON, default=list)  # List of practice areas
    years_experience = Column(Integer, nullable=True)
    
    bio = Column(Text, nullable=True)
    consultation_fee = Column(Integer, nullable=True)  # In cents
    accepts_new_clients = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<LawyerProfile for user {self.user_id}>"
