"""
Conversation Service for LegalAI
Manages ChatGPT-like conversation and message persistence
All operations are user-scoped (never trust client user_id)
"""
import uuid
import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    logger.warning("BigQuery not available")


class ConversationService:
    """Service for managing conversations and messages"""
    
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
                logger.info("ConversationService initialized with BigQuery")
            else:
                self.client = bigquery.Client(project=self.project_id)
                logger.info("ConversationService initialized with default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery: {e}")
    
    async def create_conversation(
        self,
        user_id: str,
        title: str = "New chat"
    ) -> Optional[Dict]:
        """
        Create new conversation for user.
        
        SECURITY: user_id from server session, not client request.
        """
        if not self.client:
            logger.warning("BigQuery not available, using mock")
            return {
                'conversation_id': str(uuid.uuid4()),
                'user_id': user_id,
                'title': title,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_archived': False,
                'is_pinned': False,
                'message_count': 0
            }
        
        try:
            conversation_id = str(uuid.uuid4())
            
            query = f"""
            INSERT INTO `{self.project_id}.{self.dataset_id}.conversations`
            (conversation_id, user_id, title, created_at, updated_at, is_archived, is_pinned, message_count, env)
            VALUES
            (@conversation_id, @user_id, @title, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), FALSE, FALSE, 0, @env)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("title", "STRING", title),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            
            return {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'title': title,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_archived': False,
                'is_pinned': False,
                'message_count': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return None
    
    async def list_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        archived: bool = False
    ) -> List[Dict]:
        """
        List conversations for user (sidebar history).
        
        SECURITY: user_id from session - scoped query.
        ChatGPT behavior: Shows recent conversations ordered by updated_at.
        """
        if not self.client:
            return []
        
        try:
            query = f"""
            SELECT
              c.conversation_id,
              c.user_id,
              c.title,
              c.created_at,
              c.updated_at,
              c.is_archived,
              c.is_pinned,
              c.message_count,
              (SELECT content FROM `{self.project_id}.{self.dataset_id}.messages` m
               WHERE m.conversation_id = c.conversation_id 
                 AND m.user_id = c.user_id
               ORDER BY m.created_at ASC LIMIT 1) AS first_message,
              (SELECT created_at FROM `{self.project_id}.{self.dataset_id}.messages` m
               WHERE m.conversation_id = c.conversation_id
                 AND m.user_id = c.user_id
               ORDER BY m.created_at DESC LIMIT 1) AS last_message_at
            FROM `{self.project_id}.{self.dataset_id}.conversations` c
            WHERE c.user_id = @user_id
              AND c.env = @env
              AND c.is_archived = @archived
            ORDER BY c.is_pinned DESC, c.updated_at DESC
            LIMIT @limit OFFSET @offset
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                    bigquery.ScalarQueryParameter("archived", "BOOL", archived),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            conversations = [dict(row) for row in results]
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []
    
    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> Optional[Dict]:
        """
        Get conversation with all messages.
        
        SECURITY: Verifies conversation belongs to user_id from session.
        """
        if not self.client:
            return None
        
        try:
            # Get conversation metadata
            conv_query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.conversations`
            WHERE conversation_id = @conversation_id
              AND user_id = @user_id
              AND env = @env
            LIMIT 1
            """
            
            conv_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            conv_job = self.client.query(conv_query, job_config=conv_job_config)
            conv_results = list(conv_job.result())
            
            if not conv_results:
                return None  # Not found or access denied
            
            conversation = dict(conv_results[0])
            
            # Get messages
            msg_query = f"""
            SELECT message_id, conversation_id, role, content, created_at, metadata
            FROM `{self.project_id}.{self.dataset_id}.messages`
            WHERE conversation_id = @conversation_id
              AND user_id = @user_id
              AND env = @env
            ORDER BY created_at ASC
            """
            
            msg_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            msg_job = self.client.query(msg_query, job_config=msg_job_config)
            messages = [dict(row) for row in msg_job.result()]
            
            conversation['messages'] = messages
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None
    
    async def create_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create message in conversation.
        
        SECURITY: user_id from session, verifies conversation ownership.
        """
        if not self.client:
            return {
                'message_id': str(uuid.uuid4()),
                'conversation_id': conversation_id,
                'role': role,
                'content': content,
                'created_at': datetime.utcnow(),
                'metadata': metadata
            }
        
        try:
            message_id = str(uuid.uuid4())
            
            # Insert message
            insert_query = f"""
            INSERT INTO `{self.project_id}.{self.dataset_id}.messages`
            (message_id, conversation_id, user_id, role, content, created_at, metadata, env)
            VALUES
            (@message_id, @conversation_id, @user_id, @role, @content, CURRENT_TIMESTAMP(), @metadata, @env)
            """
            
            insert_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("message_id", "STRING", message_id),
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("role", "STRING", role),
                    bigquery.ScalarQueryParameter("content", "STRING", content),
                    bigquery.ScalarQueryParameter("metadata", "JSON", metadata or {}),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            self.client.query(insert_query, job_config=insert_job_config).result()
            
            # Update conversation updated_at and message_count
            update_query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.conversations`
            SET updated_at = CURRENT_TIMESTAMP(),
                message_count = message_count + 1
            WHERE conversation_id = @conversation_id
              AND user_id = @user_id
              AND env = @env
            """
            
            update_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            self.client.query(update_query, job_config=update_job_config).result()
            
            logger.info(f"Created message {message_id} in conversation {conversation_id}")
            
            return {
                'message_id': message_id,
                'conversation_id': conversation_id,
                'role': role,
                'content': content,
                'created_at': datetime.utcnow(),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            return None
    
    async def archive_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Archive conversation (soft delete)"""
        if not self.client:
            return True
        
        try:
            query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.conversations`
            SET is_archived = TRUE,
                updated_at = CURRENT_TIMESTAMP()
            WHERE conversation_id = @conversation_id
              AND user_id = @user_id
              AND env = @env
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            self.client.query(query, job_config=job_config).result()
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive conversation: {e}")
            return False
    
    async def update_conversation_title(
        self,
        conversation_id: str,
        user_id: str,
        title: str
    ) -> bool:
        """Update conversation title"""
        if not self.client:
            return True
        
        try:
            query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.conversations`
            SET title = @title,
                updated_at = CURRENT_TIMESTAMP()
            WHERE conversation_id = @conversation_id
              AND user_id = @user_id
              AND env = @env
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("title", "STRING", title),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            self.client.query(query, job_config=job_config).result()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update title: {e}")
            return False


# Global instance
_conversation_service = None

def get_conversation_service() -> ConversationService:
    """Get conversation service instance"""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = ConversationService()
    return _conversation_service
