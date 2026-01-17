"""
Search Service for LegalAI
User-scoped full-text search across conversations, messages, and attachments
"""
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    logger.warning("BigQuery not available")


class SearchService:
    """Service for user-scoped search"""
    
    def __init__(self):
        self.client = None
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'legalai')
        self.env = os.getenv('ENVIRONMENT', 'dev')
        self._initialize()
    
    def _initialize(self):
        """Initialize BigQuery client"""
        if not BIGQUERY_AVAILABLE:
            return
        
        try:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
            else:
                self.client = bigquery.Client(project=self.project_id)
            
            logger.info("Search service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize search service: {e}")
    
    async def search(
        self,
        query: str,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        Search user's conversations, messages, and attachments.
        
        SECURITY: All results scoped to user_id from server session.
        
        Returns results ranked by relevance (simple LIKE for now).
        """
        if not self.client:
            logger.warning("BigQuery not available, returning empty results")
            return []
        
        try:
            # Normalize query for LIKE matching
            search_term = f"%{query.lower()}%"
            
            # Search across conversations, messages, and attachments
            # CRITICAL: ALL WHERE clauses include user_id scoping
            search_query = f"""
            -- Search in conversation titles
            SELECT
              'conversation' AS result_type,
              c.conversation_id,
              NULL AS message_id,
              NULL AS attachment_id,
              c.title,
              SUBSTR(c.title, 1, 200) AS snippet,
              c.created_at,
              2.0 AS relevance_score  -- Higher score for title matches
            FROM `{self.project_id}.{self.dataset_id}.conversations` c
            WHERE c.user_id = @user_id
              AND c.env = @env
              AND c.is_archived = FALSE
              AND LOWER(c.title) LIKE @search_term
            
            UNION ALL
            
            -- Search in message content
            SELECT
              'message' AS result_type,
              m.conversation_id,
              m.message_id,
              NULL AS attachment_id,
              c.title,
              SUBSTR(m.content, 1, 200) AS snippet,
              m.created_at,
              1.0 AS relevance_score
            FROM `{self.project_id}.{self.dataset_id}.messages` m
            JOIN `{self.project_id}.{self.dataset_id}.conversations` c
              ON m.conversation_id = c.conversation_id
              AND m.user_id = c.user_id
              AND m.env = c.env
            WHERE m.user_id = @user_id
              AND m.env = @env
              AND LOWER(m.content) LIKE @search_term
            
            UNION ALL
            
            -- Search in attachment metadata (OCR text if available)
            SELECT
              'attachment' AS result_type,
              a.conversation_id,
              NULL AS message_id,
              a.attachment_id,
              a.file_name AS title,
              COALESCE(
                JSON_EXTRACT_SCALAR(a.metadata, '$.ocr_text'),
                a.file_name
              ) AS snippet,
              a.uploaded_at AS created_at,
              0.8 AS relevance_score
            FROM `{self.project_id}.{self.dataset_id}.attachments` a
            WHERE a.user_id = @user_id
              AND a.env = @env
              AND a.status = 'completed'
              AND (
                LOWER(a.file_name) LIKE @search_term
                OR LOWER(JSON_EXTRACT_SCALAR(a.metadata, '$.ocr_text')) LIKE @search_term
              )
            
            ORDER BY relevance_score DESC, created_at DESC
            LIMIT @limit OFFSET @offset
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                    bigquery.ScalarQueryParameter("search_term", "STRING", search_term),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset),
                ]
            )
            
            query_job = self.client.query(search_query, job_config=job_config)
            results = list(query_job.result())
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []


# Global instance
_search_service = None

def get_search_service() -> SearchService:
    """Get search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
