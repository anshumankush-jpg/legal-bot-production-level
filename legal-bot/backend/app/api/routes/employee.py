"""Employee portal API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.database import get_db
from app.models.db_models import (
    User, UserRole, MatterDB, Message, Document,
    EmployeeAssignment, AuditLog
)
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/employee", tags=["employee"])


# Request/Response Models

class AssignedMatterResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    user_email: str
    created_at: str
    updated_at: str
    message_count: int
    document_count: int


class MatterDetailResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    user_id: str
    user_email: str
    user_name: Optional[str]
    created_at: str
    updated_at: str
    jurisdiction_data: dict
    structured_data: dict


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: Optional[str]
    file_size: Optional[int]
    document_type: Optional[str]
    created_at: str


class AssignEmployeeRequest(BaseModel):
    matter_id: str
    employee_user_id: str


# Helper Functions

def check_employee_role(user: User):
    """Check if user is employee or employee_admin."""
    if user.role not in [UserRole.EMPLOYEE, UserRole.EMPLOYEE_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee or Employee Admin access required"
        )


def check_employee_admin_role(user: User):
    """Check if user is employee_admin."""
    if user.role != UserRole.EMPLOYEE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee Admin access required"
        )


def check_matter_access(db: Session, user: User, matter_id: str) -> bool:
    """Check if employee has access to a matter."""
    if user.role == UserRole.EMPLOYEE_ADMIN:
        return True  # Admin can see all matters
    
    # Check if employee is assigned to this matter
    assignment = db.query(EmployeeAssignment).filter(
        EmployeeAssignment.employee_user_id == user.id,
        EmployeeAssignment.matter_id == matter_id,
        EmployeeAssignment.revoked_at.is_(None)
    ).first()
    
    return assignment is not None


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


# Employee Dashboard Endpoints

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee dashboard summary."""
    check_employee_role(current_user)
    
    # Get assigned matters count
    if current_user.role == UserRole.EMPLOYEE_ADMIN:
        total_matters = db.query(MatterDB).count()
        assigned_matters_count = total_matters
    else:
        assigned_matters = db.query(EmployeeAssignment).filter(
            EmployeeAssignment.employee_user_id == current_user.id,
            EmployeeAssignment.revoked_at.is_(None)
        ).count()
        assigned_matters_count = assigned_matters
    
    return {
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role.value
        },
        "stats": {
            "assigned_matters": assigned_matters_count,
            "role": current_user.role.value
        }
    }


@router.get("/matters", response_model=List[AssignedMatterResponse])
async def get_assigned_matters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50
):
    """Get matters assigned to this employee."""
    check_employee_role(current_user)
    
    # Build query
    if current_user.role == UserRole.EMPLOYEE_ADMIN:
        # Admin can see all matters
        query = db.query(MatterDB)
    else:
        # Get assigned matters only
        assigned_matter_ids = db.query(EmployeeAssignment.matter_id).filter(
            EmployeeAssignment.employee_user_id == current_user.id,
            EmployeeAssignment.revoked_at.is_(None)
        ).subquery()
        
        query = db.query(MatterDB).filter(MatterDB.id.in_(assigned_matter_ids))
    
    # Apply status filter
    if status_filter:
        query = query.filter(MatterDB.status == status_filter)
    
    # Get matters
    matters = query.order_by(MatterDB.updated_at.desc()).offset(skip).limit(limit).all()
    
    # Build response
    result = []
    for matter in matters:
        # Get user email
        user = db.query(User).filter(User.id == matter.user_id).first()
        
        # Count messages and documents
        message_count = db.query(Message).filter(Message.matter_id == matter.id).count()
        document_count = db.query(Document).filter(Document.matter_id == matter.id).count()
        
        result.append(AssignedMatterResponse(
            id=matter.id,
            title=matter.title,
            description=matter.description,
            status=matter.status,
            user_email=user.email if user else "Unknown",
            created_at=matter.created_at.isoformat(),
            updated_at=matter.updated_at.isoformat(),
            message_count=message_count,
            document_count=document_count
        ))
    
    return result


@router.get("/matters/{matter_id}", response_model=MatterDetailResponse)
async def get_matter_detail(
    matter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a matter."""
    check_employee_role(current_user)
    
    # Check access
    if not check_matter_access(db, current_user, matter_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this matter"
        )
    
    # Get matter
    matter = db.query(MatterDB).filter(MatterDB.id == matter_id).first()
    if not matter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matter not found"
        )
    
    # Get user
    user = db.query(User).filter(User.id == matter.user_id).first()
    
    # Log audit
    log_audit(db, current_user.id, "MATTER_VIEWED", {"matter_id": matter_id})
    
    return MatterDetailResponse(
        id=matter.id,
        title=matter.title,
        description=matter.description,
        status=matter.status,
        user_id=matter.user_id,
        user_email=user.email if user else "Unknown",
        user_name=user.name if user else None,
        created_at=matter.created_at.isoformat(),
        updated_at=matter.updated_at.isoformat(),
        jurisdiction_data=matter.jurisdiction_data or {},
        structured_data=matter.structured_data or {}
    )


@router.get("/matters/{matter_id}/messages", response_model=List[ChatMessageResponse])
async def get_matter_messages(
    matter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """Get chat messages for a matter."""
    check_employee_role(current_user)
    
    # Check access
    if not check_matter_access(db, current_user, matter_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this matter"
        )
    
    # Get messages
    messages = db.query(Message).filter(
        Message.matter_id == matter_id
    ).order_by(Message.created_at.asc()).limit(limit).all()
    
    # Log audit
    log_audit(db, current_user.id, "MESSAGE_VIEWED", {"matter_id": matter_id, "count": len(messages)})
    
    return [
        ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]


@router.get("/matters/{matter_id}/documents", response_model=List[DocumentResponse])
async def get_matter_documents(
    matter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get documents for a matter."""
    check_employee_role(current_user)
    
    # Check access
    if not check_matter_access(db, current_user, matter_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this matter"
        )
    
    # Get documents
    documents = db.query(Document).filter(
        Document.matter_id == matter_id
    ).order_by(Document.created_at.desc()).all()
    
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            document_type=doc.document_type,
            created_at=doc.created_at.isoformat()
        )
        for doc in documents
    ]


# Admin-only: Assignment Management

@router.post("/assignments")
async def assign_employee_to_matter(
    request_data: AssignEmployeeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign an employee to a matter (admin only)."""
    check_employee_admin_role(current_user)
    
    # Check if matter exists
    matter = db.query(MatterDB).filter(MatterDB.id == request_data.matter_id).first()
    if not matter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matter not found"
        )
    
    # Check if employee exists
    employee = db.query(User).filter(User.id == request_data.employee_user_id).first()
    if not employee or employee.role not in [UserRole.EMPLOYEE, UserRole.EMPLOYEE_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee user"
        )
    
    # Check if assignment already exists
    existing = db.query(EmployeeAssignment).filter(
        EmployeeAssignment.employee_user_id == request_data.employee_user_id,
        EmployeeAssignment.matter_id == request_data.matter_id,
        EmployeeAssignment.revoked_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment already exists"
        )
    
    # Create assignment
    assignment = EmployeeAssignment(
        employee_user_id=request_data.employee_user_id,
        matter_id=request_data.matter_id,
        assigned_by_user_id=current_user.id
    )
    db.add(assignment)
    db.commit()
    
    # Log audit
    log_audit(db, current_user.id, "EMPLOYEE_ASSIGNED", {
        "employee_id": request_data.employee_user_id,
        "matter_id": request_data.matter_id
    })
    
    return {"message": "Employee assigned successfully", "assignment_id": assignment.id}


@router.delete("/assignments/{assignment_id}")
async def revoke_employee_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke an employee assignment (admin only)."""
    check_employee_admin_role(current_user)
    
    # Get assignment
    assignment = db.query(EmployeeAssignment).filter(
        EmployeeAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Revoke
    assignment.revoked_at = datetime.utcnow()
    db.commit()
    
    # Log audit
    log_audit(db, current_user.id, "EMPLOYEE_UNASSIGNED", {
        "assignment_id": assignment_id,
        "matter_id": assignment.matter_id
    })
    
    return {"message": "Assignment revoked successfully"}
