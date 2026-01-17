"""
Storage Service for LegalAI
Manages file uploads to Google Cloud Storage with user scoping
"""
import os
import uuid
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from google.cloud import storage, bigquery
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logger.warning("Google Cloud Storage not available")


class StorageService:
    """Service for managing file uploads and attachments"""
    
    def __init__(self):
        self.storage_client = None
        self.bq_client = None
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'legalai-attachments')
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'legalai')
        self.env = os.getenv('ENVIRONMENT', 'dev')
        self._initialize()
    
    def _initialize(self):
        """Initialize GCS and BigQuery clients"""
        if not GCS_AVAILABLE:
            return
        
        try:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.storage_client = storage.Client(
                    credentials=credentials,
                    project=self.project_id
                )
                self.bq_client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
                logger.info(f"Storage service initialized with bucket: {self.bucket_name}")
            else:
                self.storage_client = storage.Client(project=self.project_id)
                self.bq_client = bigquery.Client(project=self.project_id)
                logger.info("Storage service initialized with default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
    
    async def generate_signed_upload_url(
        self,
        path: str,
        content_type: str,
        expires_minutes: int = 15
    ) -> Optional[Dict]:
        """
        Generate signed URL for direct client upload to GCS.
        
        Returns:
            {
                'signed_url': str,  # URL for client to PUT file
                'gcs_url': str,     # gs://bucket/path
                'expires_at': datetime
            }
        """
        if not self.storage_client:
            logger.warning("GCS not available, returning mock signed URL")
            return {
                'signed_url': f'https://storage.googleapis.com/mock-upload/{path}',
                'gcs_url': f'gs://{self.bucket_name}/{path}',
                'expires_at': datetime.utcnow() + timedelta(minutes=expires_minutes)
            }
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(path)
            
            # Generate signed URL for PUT (upload)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expires_minutes),
                method="PUT",
                content_type=content_type
            )
            
            gcs_url = f"gs://{self.bucket_name}/{path}"
            expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
            
            return {
                'signed_url': signed_url,
                'gcs_url': gcs_url,
                'expires_at': expires_at
            }
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            return None
    
    async def create_attachment_metadata(
        self,
        attachment_id: str,
        user_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        gcs_url: str,
        conversation_id: Optional[str] = None,
        status: str = 'uploading'
    ) -> bool:
        """Save attachment metadata to BigQuery"""
        if not self.bq_client:
            return True
        
        try:
            query = f"""
            INSERT INTO `{self.project_id}.{self.dataset_id}.attachments`
            (attachment_id, user_id, conversation_id, file_name, file_type, file_size,
             gcs_url, status, uploaded_at, env)
            VALUES
            (@attachment_id, @user_id, @conversation_id, @file_name, @file_type, @file_size,
             @gcs_url, @status, CURRENT_TIMESTAMP(), @env)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("attachment_id", "STRING", attachment_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("file_name", "STRING", file_name),
                    bigquery.ScalarQueryParameter("file_type", "STRING", file_type),
                    bigquery.ScalarQueryParameter("file_size", "INT64", file_size),
                    bigquery.ScalarQueryParameter("gcs_url", "STRING", gcs_url),
                    bigquery.ScalarQueryParameter("status", "STRING", status),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            self.bq_client.query(query, job_config=job_config).result()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create attachment metadata: {e}")
            return False
    
    async def confirm_upload(
        self,
        attachment_id: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        sha256: Optional[str] = None
    ) -> Optional[Dict]:
        """Confirm upload and update attachment status"""
        if not self.bq_client:
            return {
                'attachment_id': attachment_id,
                'user_id': user_id,
                'conversation_id': conversation_id,
                'file_name': 'mock.pdf',
                'file_type': 'application/pdf',
                'file_size': 1024,
                'gcs_url': f'gs://mock/{attachment_id}',
                'sha256': sha256,
                'uploaded_at': datetime.utcnow(),
                'metadata': {}
            }
        
        try:
            # Update attachment
            update_query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.attachments`
            SET status = 'completed',
                conversation_id = @conversation_id,
                sha256 = @sha256
            WHERE attachment_id = @attachment_id
              AND user_id = @user_id
              AND env = @env
            """
            
            update_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("attachment_id", "STRING", attachment_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("sha256", "STRING", sha256),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            self.bq_client.query(update_query, job_config=update_config).result()
            
            # Get updated attachment
            return await self.get_attachment(attachment_id, user_id)
            
        except Exception as e:
            logger.error(f"Failed to confirm upload: {e}")
            return None
    
    async def get_attachment(
        self,
        attachment_id: str,
        user_id: str
    ) -> Optional[Dict]:
        """Get attachment metadata (user-scoped)"""
        if not self.bq_client:
            return None
        
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.attachments`
            WHERE attachment_id = @attachment_id
              AND user_id = @user_id
              AND env = @env
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("attachment_id", "STRING", attachment_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            results = list(self.bq_client.query(query, job_config=job_config).result())
            
            if results:
                return dict(results[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get attachment: {e}")
            return None
    
    async def list_attachments(
        self,
        conversation_id: str,
        user_id: str
    ) -> List[Dict]:
        """List attachments for conversation (user-scoped)"""
        if not self.bq_client:
            return []
        
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.attachments`
            WHERE conversation_id = @conversation_id
              AND user_id = @user_id
              AND env = @env
              AND status = 'completed'
            ORDER BY uploaded_at ASC
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            results = list(self.bq_client.query(query, job_config=job_config).result())
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to list attachments: {e}")
            return []


# Global instance
_storage_service = None

def get_storage_service() -> StorageService:
    """Get storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
