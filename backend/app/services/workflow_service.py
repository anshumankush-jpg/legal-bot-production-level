"""Workflow engine for matter state management and next steps."""
import logging
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel

from app.models.matter import Matter, MatterStatus, MatterType

logger = logging.getLogger(__name__)


class WorkflowEvent(str, Enum):
    """Events that trigger workflow transitions."""
    TICKET_PARSED = "ticket_parsed"
    USER_CHOSE_OPTION_A = "user_chose_option_A"
    USER_CHOSE_OPTION_B = "user_chose_option_B"
    USER_CHOSE_OPTION_C = "user_chose_option_C"
    DISCLOSURE_REQUESTED = "disclosure_requested"
    DOCUMENTS_GENERATED = "documents_generated"
    REMINDER_SET = "reminder_set"
    COURT_DATE_SET = "court_date_set"
    MATTER_CLOSED = "matter_closed"


class NextStep(BaseModel):
    """A suggested next step in the workflow."""
    step_id: str
    label: str
    description: str
    action_type: str  # e.g., "explain_options", "generate_document", "set_reminder", "ask_questions"
    priority: int = 1  # 1 = high, 2 = medium, 3 = low
    required: bool = False


class WorkflowService:
    """Service for managing matter workflows and suggesting next steps."""
    
    def __init__(self):
        """Initialize workflow service with state machine definitions."""
        self.workflows = self._define_workflows()
    
    def _define_workflows(self) -> Dict[MatterType, Dict]:
        """Define state machines for each matter type."""
        return {
            MatterType.TRAFFIC_TICKET: {
                "states": [
                    MatterStatus.NEW,
                    MatterStatus.PARSED,
                    MatterStatus.OPTIONS_EXPLAINED,
                    MatterStatus.WAITING_FOR_DISCLOSURE,
                    MatterStatus.DOCUMENTS_GENERATED,
                    MatterStatus.REMINDER_SET,
                    MatterStatus.COURT_SCHEDULED,
                    MatterStatus.CLOSED
                ],
                "transitions": {
                    MatterStatus.NEW: {
                        WorkflowEvent.TICKET_PARSED: MatterStatus.PARSED
                    },
                    MatterStatus.PARSED: {
                        WorkflowEvent.USER_CHOSE_OPTION_A: MatterStatus.OPTIONS_EXPLAINED,
                        WorkflowEvent.USER_CHOSE_OPTION_B: MatterStatus.OPTIONS_EXPLAINED,
                        WorkflowEvent.USER_CHOSE_OPTION_C: MatterStatus.OPTIONS_EXPLAINED
                    },
                    MatterStatus.OPTIONS_EXPLAINED: {
                        WorkflowEvent.DISCLOSURE_REQUESTED: MatterStatus.WAITING_FOR_DISCLOSURE,
                        WorkflowEvent.DOCUMENTS_GENERATED: MatterStatus.DOCUMENTS_GENERATED
                    },
                    MatterStatus.WAITING_FOR_DISCLOSURE: {
                        WorkflowEvent.DOCUMENTS_GENERATED: MatterStatus.DOCUMENTS_GENERATED
                    },
                    MatterStatus.DOCUMENTS_GENERATED: {
                        WorkflowEvent.REMINDER_SET: MatterStatus.REMINDER_SET,
                        WorkflowEvent.COURT_DATE_SET: MatterStatus.COURT_SCHEDULED
                    },
                    MatterStatus.REMINDER_SET: {
                        WorkflowEvent.COURT_DATE_SET: MatterStatus.COURT_SCHEDULED
                    },
                    MatterStatus.COURT_SCHEDULED: {
                        WorkflowEvent.MATTER_CLOSED: MatterStatus.CLOSED
                    }
                }
            },
            MatterType.PARKING_TICKET: {
                "states": [
                    MatterStatus.NEW,
                    MatterStatus.PARSED,
                    MatterStatus.OPTIONS_EXPLAINED,
                    MatterStatus.DOCUMENTS_GENERATED,
                    MatterStatus.CLOSED
                ],
                "transitions": {
                    MatterStatus.NEW: {
                        WorkflowEvent.TICKET_PARSED: MatterStatus.PARSED
                    },
                    MatterStatus.PARSED: {
                        WorkflowEvent.USER_CHOSE_OPTION_A: MatterStatus.OPTIONS_EXPLAINED,
                        WorkflowEvent.USER_CHOSE_OPTION_B: MatterStatus.OPTIONS_EXPLAINED
                    },
                    MatterStatus.OPTIONS_EXPLAINED: {
                        WorkflowEvent.DOCUMENTS_GENERATED: MatterStatus.DOCUMENTS_GENERATED
                    },
                    MatterStatus.DOCUMENTS_GENERATED: {
                        WorkflowEvent.MATTER_CLOSED: MatterStatus.CLOSED
                    }
                }
            },
            MatterType.BYLAW_FINE: {
                "states": [
                    MatterStatus.NEW,
                    MatterStatus.PARSED,
                    MatterStatus.OPTIONS_EXPLAINED,
                    MatterStatus.DOCUMENTS_GENERATED,
                    MatterStatus.CLOSED
                ],
                "transitions": {
                    MatterStatus.NEW: {
                        WorkflowEvent.TICKET_PARSED: MatterStatus.PARSED
                    },
                    MatterStatus.PARSED: {
                        WorkflowEvent.USER_CHOSE_OPTION_A: MatterStatus.OPTIONS_EXPLAINED,
                        WorkflowEvent.USER_CHOSE_OPTION_B: MatterStatus.OPTIONS_EXPLAINED
                    },
                    MatterStatus.OPTIONS_EXPLAINED: {
                        WorkflowEvent.DOCUMENTS_GENERATED: MatterStatus.DOCUMENTS_GENERATED
                    },
                    MatterStatus.DOCUMENTS_GENERATED: {
                        WorkflowEvent.MATTER_CLOSED: MatterStatus.CLOSED
                    }
                }
            }
        }
    
    def get_next_steps(self, matter: Matter) -> List[NextStep]:
        """
        Get suggested next steps for a matter based on its current state.
        
        Args:
            matter: The matter to analyze
            
        Returns:
            List of suggested next steps
        """
        workflow = self.workflows.get(matter.matter_type)
        if not workflow:
            return []
        
        steps = []
        current_status = matter.status
        
        # Define next steps based on current state
        if current_status == MatterStatus.NEW:
            steps.append(NextStep(
                step_id="parse_ticket",
                label="Parse Ticket Information",
                description="Extract key information from the ticket or summons",
                action_type="parse_document",
                priority=1,
                required=True
            ))
        
        elif current_status == MatterStatus.PARSED:
            steps.append(NextStep(
                step_id="explain_options",
                label="Explain Your Options",
                description="Get personalized advice on how to proceed with your case",
                action_type="explain_options",
                priority=1,
                required=True
            ))
        
        elif current_status == MatterStatus.OPTIONS_EXPLAINED:
            steps.append(NextStep(
                step_id="request_disclosure",
                label="Request Disclosure",
                description="Generate a disclosure request letter to get more information",
                action_type="generate_document",
                priority=1,
                required=False
            ))
            steps.append(NextStep(
                step_id="generate_response",
                label="Generate Response Documents",
                description="Create necessary documents for your chosen option",
                action_type="generate_document",
                priority=2,
                required=False
            ))
        
        elif current_status == MatterStatus.WAITING_FOR_DISCLOSURE:
            steps.append(NextStep(
                step_id="review_disclosure",
                label="Review Received Disclosure",
                description="Upload and analyze disclosure documents when received",
                action_type="review_documents",
                priority=1,
                required=False
            ))
        
        elif current_status == MatterStatus.DOCUMENTS_GENERATED:
            steps.append(NextStep(
                step_id="set_reminder",
                label="Set Court Date Reminder",
                description="Set a reminder for important dates and deadlines",
                action_type="set_reminder",
                priority=1,
                required=False
            ))
        
        elif current_status == MatterStatus.COURT_SCHEDULED:
            steps.append(NextStep(
                step_id="prepare_for_court",
                label="Prepare for Court",
                description="Review your case and prepare for the court appearance",
                action_type="prepare",
                priority=1,
                required=False
            ))
        
        return steps
    
    def process_event(self, matter: Matter, event: WorkflowEvent) -> Optional[MatterStatus]:
        """
        Process a workflow event and return the new status if transition is valid.
        
        Args:
            matter: The matter
            event: The event that occurred
            
        Returns:
            New status if transition is valid, None otherwise
        """
        workflow = self.workflows.get(matter.matter_type)
        if not workflow:
            return None
        
        transitions = workflow.get("transitions", {})
        current_transitions = transitions.get(matter.status, {})
        new_status = current_transitions.get(event)
        
        if new_status:
            logger.info(f"Matter {matter.matter_id} transitioned from {matter.status} to {new_status} via {event}")
            return new_status
        
        logger.warning(f"Invalid transition for matter {matter.matter_id}: {matter.status} -> {event}")
        return None


# Global singleton instance
_workflow_service: Optional[WorkflowService] = None


def get_workflow_service() -> WorkflowService:
    """Get or create the global workflow service instance."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService()
    return _workflow_service

