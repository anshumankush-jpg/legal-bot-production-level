"""Analytics service for tracking usage, feedback, and metrics."""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.config import settings

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking analytics and metrics."""
    
    def __init__(self):
        """Initialize analytics service."""
        # In-memory storage (replace with Firestore/Cloud SQL in production)
        self.metrics = {
            'users_by_day': defaultdict(set),  # {date: set of user_ids}
            'messages_by_day': defaultdict(int),  # {date: count}
            'feedback': {
                'positive': 0,
                'negative': 0,
                'total': 0
            },
            'confidence_levels': {
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'citation_counts': defaultdict(int),  # {source: count}
            'queries': []  # List of query logs
        }
    
    def track_user_activity(self, user_id: str, date: Optional[datetime] = None):
        """Track unique user activity."""
        if date is None:
            date = datetime.utcnow()
        date_str = date.strftime('%Y-%m-%d')
        self.metrics['users_by_day'][date_str].add(user_id)
        logger.debug(f"Tracked user activity: {user_id} on {date_str}")
    
    def track_message(self, date: Optional[datetime] = None):
        """Track message count."""
        if date is None:
            date = datetime.utcnow()
        date_str = date.strftime('%Y-%m-%d')
        self.metrics['messages_by_day'][date_str] += 1
        logger.debug(f"Tracked message on {date_str}")
    
    def track_feedback(self, is_positive: bool):
        """Track user feedback."""
        if is_positive:
            self.metrics['feedback']['positive'] += 1
        else:
            self.metrics['feedback']['negative'] += 1
        self.metrics['feedback']['total'] += 1
        logger.debug(f"Tracked feedback: {'positive' if is_positive else 'negative'}")
    
    def track_confidence(self, level: str):
        """Track confidence level (high, medium, low)."""
        if level in ['high', 'medium', 'low']:
            self.metrics['confidence_levels'][level] += 1
            logger.debug(f"Tracked confidence level: {level}")
    
    def track_citation(self, source: str):
        """Track document citation."""
        self.metrics['citation_counts'][source] += 1
        logger.debug(f"Tracked citation: {source}")
    
    def track_query(self, query: str, response_time: float, sources: List[str]):
        """Track query for analytics."""
        self.metrics['queries'].append({
            'query': query,
            'response_time': response_time,
            'sources': sources,
            'timestamp': datetime.utcnow().isoformat()
        })
        # Keep only last 1000 queries
        if len(self.metrics['queries']) > 1000:
            self.metrics['queries'] = self.metrics['queries'][-1000:]
    
    def get_unique_users_by_day(self, days: int = 30) -> Dict[str, int]:
        """Get unique users per day for last N days."""
        result = {}
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            result[date_str] = len(self.metrics['users_by_day'].get(date_str, set()))
        return result
    
    def get_messages_by_day(self, days: int = 30) -> Dict[str, int]:
        """Get message count per day for last N days."""
        result = {}
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            result[date_str] = self.metrics['messages_by_day'].get(date_str, 0)
        return result
    
    def get_feedback_percentage(self) -> Dict[str, float]:
        """Get feedback percentages."""
        total = self.metrics['feedback']['total']
        if total == 0:
            return {'positive': 0.0, 'negative': 0.0}
        
        return {
            'positive': (self.metrics['feedback']['positive'] / total) * 100,
            'negative': (self.metrics['feedback']['negative'] / total) * 100
        }
    
    def get_confidence_distribution(self) -> Dict[str, int]:
        """Get confidence level distribution."""
        return self.metrics['confidence_levels'].copy()
    
    def get_top_cited_documents(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get most cited documents."""
        sorted_citations = sorted(
            self.metrics['citation_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {'source': source, 'count': count}
            for source, count in sorted_citations[:limit]
        ]
    
    def get_analytics_summary(self) -> Dict:
        """Get complete analytics summary."""
        return {
            'unique_users_by_day': self.get_unique_users_by_day(30),
            'messages_by_day': self.get_messages_by_day(30),
            'feedback_percentages': self.get_feedback_percentage(),
            'confidence_distribution': self.get_confidence_distribution(),
            'top_cited_documents': self.get_top_cited_documents(10),
            'total_queries': len(self.metrics['queries']),
            'total_feedback': self.metrics['feedback']['total']
        }


# Global singleton instance
_analytics_service: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """Get or create the global analytics service instance."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service

