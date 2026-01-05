"""Endpoints for managing matters/cases."""
import logging
from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional, List

from app.models.matter import (
    CreateMatterRequest,
    UpdateMatterRequest,
    MatterResponse,
    MatterType,
    MatterStatus
)
from app.services.matter_service import get_matter_service
from app.services.workflow_service import get_workflow_service, WorkflowEvent, NextStep
from app.services.playbook_service import get_playbook_service, PlaybookResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matters", tags=["matters"])


@router.post("", response_model=MatterResponse)
async def create_matter(request: CreateMatterRequest):
    """
    Create a new matter/case.
    
    Body:
    - user_id: Optional user identifier
    - session_id: Optional session identifier (for anonymous users)
    - jurisdiction: {country, region, region_code}
    - matter_type: Type of matter (traffic_ticket, parking_ticket, etc.)
    - structured_data: Optional parsed ticket fields
    """
    try:
        matter_service = get_matter_service()
        matter = matter_service.create_matter(request)
        
        return MatterResponse(
            matter_id=matter.matter_id,
            user_id=matter.user_id,
            session_id=matter.session_id,
            jurisdiction=matter.jurisdiction,
            matter_type=matter.matter_type.value,
            status=matter.status.value,
            raw_documents=matter.raw_documents,
            structured_data=matter.structured_data,
            created_at=matter.created_at.isoformat(),
            updated_at=matter.updated_at.isoformat(),
            metadata=matter.metadata
        )
    except Exception as e:
        logger.error(f"Error creating matter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{matter_id}", response_model=MatterResponse)
async def get_matter(matter_id: str = Path(..., description="Matter ID")):
    """Get a matter by ID."""
    matter_service = get_matter_service()
    matter = matter_service.get_matter(matter_id)
    
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    
    return MatterResponse(
        matter_id=matter.matter_id,
        user_id=matter.user_id,
        session_id=matter.session_id,
        jurisdiction=matter.jurisdiction,
        matter_type=matter.matter_type.value,
        status=matter.status.value,
        raw_documents=matter.raw_documents,
        structured_data=matter.structured_data,
        created_at=matter.created_at.isoformat(),
        updated_at=matter.updated_at.isoformat(),
        metadata=matter.metadata
    )


@router.put("/{matter_id}", response_model=MatterResponse)
async def update_matter(
    matter_id: str = Path(..., description="Matter ID"),
    request: UpdateMatterRequest = None
):
    """Update a matter."""
    matter_service = get_matter_service()
    matter = matter_service.update_matter(matter_id, request or UpdateMatterRequest())
    
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    
    return MatterResponse(
        matter_id=matter.matter_id,
        user_id=matter.user_id,
        session_id=matter.session_id,
        jurisdiction=matter.jurisdiction,
        matter_type=matter.matter_type.value,
        status=matter.status.value,
        raw_documents=matter.raw_documents,
        structured_data=matter.structured_data,
        created_at=matter.created_at.isoformat(),
        updated_at=matter.updated_at.isoformat(),
        metadata=matter.metadata
    )


@router.get("", response_model=List[MatterResponse])
async def list_matters(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    matter_type: Optional[MatterType] = Query(None, description="Filter by matter type"),
    status: Optional[MatterStatus] = Query(None, description="Filter by status")
):
    """List matters with optional filters."""
    try:
        matter_service = get_matter_service()
        matters = matter_service.list_matters(
            user_id=user_id,
            session_id=session_id,
            matter_type=matter_type,
            status=status
        )
        
        return [
            MatterResponse(
                matter_id=m.matter_id,
                user_id=m.user_id,
                session_id=m.session_id,
                jurisdiction=m.jurisdiction,
                matter_type=m.matter_type.value,
                status=m.status.value,
                raw_documents=m.raw_documents,
                structured_data=m.structured_data,
                created_at=m.created_at.isoformat(),
                updated_at=m.updated_at.isoformat(),
                metadata=m.metadata
            )
            for m in matters
        ]
    except Exception as e:
        logger.error(f"Error listing matters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{matter_id}/next-steps")
async def get_next_steps(matter_id: str = Path(..., description="Matter ID")):
    """
    Get suggested next steps for a matter based on workflow state.
    
    Returns:
    - List of next steps with actions and priorities
    """
    try:
        matter_service = get_matter_service()
        workflow_service = get_workflow_service()
        
        matter = matter_service.get_matter(matter_id)
        if not matter:
            raise HTTPException(status_code=404, detail="Matter not found")
        
        next_steps = workflow_service.get_next_steps(matter)
        
        return {
            "matter_id": matter_id,
            "current_status": matter.status.value,
            "next_steps": [
                {
                    "step_id": step.step_id,
                    "label": step.label,
                    "description": step.description,
                    "action_type": step.action_type,
                    "priority": step.priority,
                    "required": step.required
                }
                for step in next_steps
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next steps: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{matter_id}/playbook", response_model=PlaybookResponse)
async def get_playbook(
    matter_id: str = Path(..., description="Matter ID"),
    language: str = Query("en", description="Language code (en, fr, hi, pa, es, ta, zh)")
):
    """
    Generate playbook options for a matter.
    
    Returns structured options (A1: conservative, A2: aggressive, A3: lawyer consultation).
    Supports multiple languages.
    """
    try:
        matter_service = get_matter_service()
        playbook_service = get_playbook_service()
        
        matter = matter_service.get_matter(matter_id)
        if not matter:
            raise HTTPException(status_code=404, detail="Matter not found")
        
        playbook = playbook_service.generate_playbook(matter, language=language)
        return playbook
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating playbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{matter_id}/events/{event_name}")
async def process_workflow_event(
    matter_id: str = Path(..., description="Matter ID"),
    event_name: str = Path(..., description="Event name")
):
    """
    Process a workflow event to transition matter state.
    
    Events: ticket_parsed, user_chose_option_A, user_chose_option_B, 
            disclosure_requested, documents_generated, reminder_set, 
            court_date_set, matter_closed
    """
    try:
        matter_service = get_matter_service()
        workflow_service = get_workflow_service()
        
        matter = matter_service.get_matter(matter_id)
        if not matter:
            raise HTTPException(status_code=404, detail="Matter not found")
        
        # Convert event name to enum
        try:
            event = WorkflowEvent(event_name)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event: {event_name}")
        
        # Process event
        new_status = workflow_service.process_event(matter, event)
        
        if new_status:
            # Update matter status
            updated_matter = matter_service.update_matter(
                matter_id,
                UpdateMatterRequest(status=new_status)
            )
            
            return {
                "matter_id": matter_id,
                "previous_status": matter.status.value,
                "new_status": new_status.value,
                "event": event_name,
                "success": True
            }
        else:
            return {
                "matter_id": matter_id,
                "current_status": matter.status.value,
                "event": event_name,
                "success": False,
                "message": "Invalid transition for current state"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing workflow event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

