"""Endpoints for analytics and metrics."""
import logging
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime

from app.services.analytics_service import get_analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_analytics_summary():
    """
    Get complete analytics summary.
    
    Returns:
    - Unique users by day (last 30 days)
    - Messages by day (last 30 days)
    - Feedback percentages
    - Confidence distribution
    - Top cited documents
    """
    try:
        analytics_service = get_analytics_service()
        summary = analytics_service.get_analytics_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users-by-day")
async def get_users_by_day(days: int = 30):
    """Get unique users per day for last N days."""
    try:
        analytics_service = get_analytics_service()
        return analytics_service.get_unique_users_by_day(days)
    except Exception as e:
        logger.error(f"Error getting users by day: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages-by-day")
async def get_messages_by_day(days: int = 30):
    """Get message count per day for last N days."""
    try:
        analytics_service = get_analytics_service()
        return analytics_service.get_messages_by_day(days)
    except Exception as e:
        logger.error(f"Error getting messages by day: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback")
async def get_feedback_stats():
    """Get feedback statistics."""
    try:
        analytics_service = get_analytics_service()
        return {
            'percentages': analytics_service.get_feedback_percentage(),
            'distribution': analytics_service.metrics['feedback']
        }
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(is_positive: bool):
    """Submit user feedback (thumbs up/down)."""
    try:
        analytics_service = get_analytics_service()
        analytics_service.track_feedback(is_positive)
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/confidence")
async def get_confidence_distribution():
    """Get confidence level distribution."""
    try:
        analytics_service = get_analytics_service()
        return analytics_service.get_confidence_distribution()
    except Exception as e:
        logger.error(f"Error getting confidence distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-citations")
async def get_top_citations(limit: int = 10):
    """Get most cited documents."""
    try:
        analytics_service = get_analytics_service()
        return analytics_service.get_top_cited_documents(limit)
    except Exception as e:
        logger.error(f"Error getting top citations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

