"""
BigQuery Client for LegalAI Identity and Audit
Handles user identity mapping, lawyer applications, and login events
"""
import os
import uuid
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    logger.warning("BigQuery client not installed. Install with: pip install google-cloud-bigquery")


class BigQueryIdentityClient:
    """BigQuery client for user identity and applications"""
    
    def __init__(self):
        self.client = None
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'legalai')
        self.env = os.getenv('ENVIRONMENT', 'dev')
        self._initialize()
    
    def _initialize(self):
        """Initialize BigQuery client"""
        if not BIGQUERY_AVAILABLE:
            logger.warning("BigQuery SDK not available")
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
                logger.info(f"BigQuery initialized with credentials for project: {self.project_id}")
            else:
                # Skip BigQuery if no credentials file - don't try cloud metadata (slow timeout)
                # For local development, BigQuery is optional
                logger.info("BigQuery credentials not found - BigQuery features disabled (this is OK for local dev)")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery: {e}")
            self.client = None
    
    async def upsert_identity_user(
        self,
        auth_uid: str,
        auth_provider: str,
        email: str,
        role: str,
        display_name: Optional[str] = None,
        photo_url: Optional[str] = None,
        is_verified: bool = False,
        lawyer_status: Optional[str] = None
    ) -> Optional[str]:
        """
        Upsert user identity (create or update)
        
        Args:
            auth_uid: Provider's UID
            auth_provider: google|microsoft|email
            email: User email
            role: customer|lawyer|admin
            display_name: User's display name
            photo_url: Profile photo URL
            is_verified: Email verified
            lawyer_status: not_applicable|pending|approved|rejected
            
        Returns:
            user_id (UUID) if successful
        """
        if not self.client:
            logger.warning("BigQuery not available, skipping identity upsert")
            return str(uuid.uuid4())  # Return mock ID for dev
        
        try:
            # Generate stable user_id (or fetch existing)
            user_id = str(uuid.uuid4())
            
            # Set lawyer_status based on role
            if role == 'lawyer' and not lawyer_status:
                lawyer_status = 'pending'
            elif role != 'lawyer':
                lawyer_status = 'not_applicable'
            
            # MERGE query (upsert)
            query = f"""
            MERGE `{self.project_id}.{self.dataset_id}.identity_users` AS target
            USING (
              SELECT
                @user_id AS user_id,
                @auth_provider AS auth_provider,
                @auth_uid AS auth_uid,
                @email AS email,
                @display_name AS display_name,
                @photo_url AS photo_url,
                @role AS role,
                @lawyer_status AS lawyer_status,
                TRUE AS is_active,
                @is_verified AS is_verified,
                CURRENT_TIMESTAMP() AS created_at,
                CURRENT_TIMESTAMP() AS last_login_at,
                CURRENT_TIMESTAMP() AS updated_at,
                @env AS env
            ) AS source
            ON target.auth_uid = source.auth_uid 
               AND target.auth_provider = source.auth_provider 
               AND target.env = source.env
            WHEN MATCHED THEN
              UPDATE SET
                last_login_at = source.last_login_at,
                updated_at = source.updated_at,
                display_name = source.display_name,
                photo_url = source.photo_url,
                is_verified = source.is_verified,
                role = source.role,
                lawyer_status = source.lawyer_status
            WHEN NOT MATCHED THEN
              INSERT (
                user_id, auth_provider, auth_uid, email, display_name, photo_url,
                role, lawyer_status, is_active, is_verified, created_at, last_login_at,
                updated_at, env
              )
              VALUES (
                source.user_id, source.auth_provider, source.auth_uid, source.email,
                source.display_name, source.photo_url, source.role, source.lawyer_status,
                source.is_active, source.is_verified, source.created_at, source.last_login_at,
                source.updated_at, source.env
              )
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("auth_provider", "STRING", auth_provider),
                    bigquery.ScalarQueryParameter("auth_uid", "STRING", auth_uid),
                    bigquery.ScalarQueryParameter("email", "STRING", email),
                    bigquery.ScalarQueryParameter("display_name", "STRING", display_name),
                    bigquery.ScalarQueryParameter("photo_url", "STRING", photo_url),
                    bigquery.ScalarQueryParameter("role", "STRING", role),
                    bigquery.ScalarQueryParameter("lawyer_status", "STRING", lawyer_status),
                    bigquery.ScalarQueryParameter("is_verified", "BOOL", is_verified),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()  # Wait for completion
            
            logger.info(f"Upserted user identity: {email} ({role})")
            
            # Fetch the actual user_id (in case it was an update)
            return await self.get_user_id(auth_uid, auth_provider)
            
        except Exception as e:
            logger.error(f"Failed to upsert identity user: {e}")
            return None
    
    async def get_user_id(self, auth_uid: str, auth_provider: str) -> Optional[str]:
        """Get user_id by auth_uid and provider"""
        if not self.client:
            return None
        
        try:
            query = f"""
            SELECT user_id
            FROM `{self.project_id}.{self.dataset_id}.identity_users`
            WHERE auth_uid = @auth_uid
              AND auth_provider = @auth_provider
              AND env = @env
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("auth_uid", "STRING", auth_uid),
                    bigquery.ScalarQueryParameter("auth_provider", "STRING", auth_provider),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                return results[0].user_id
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user_id: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id"""
        if not self.client:
            return None
        
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.identity_users`
            WHERE user_id = @user_id
              AND env = @env
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                return dict(results[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def update_lawyer_status(self, user_id: str, status: str) -> bool:
        """Update lawyer verification status"""
        if not self.client:
            return False
        
        try:
            query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.identity_users`
            SET lawyer_status = @status,
                updated_at = CURRENT_TIMESTAMP()
            WHERE user_id = @user_id
              AND env = @env
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("status", "STRING", status),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            
            logger.info(f"Updated lawyer status for {user_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update lawyer status: {e}")
            return False
    
    async def update_user_role(self, user_id: str, role: str, lawyer_status: str) -> bool:
        """Update user role and lawyer status"""
        if not self.client:
            return False
        
        try:
            query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.identity_users`
            SET role = @role,
                lawyer_status = @lawyer_status,
                updated_at = CURRENT_TIMESTAMP()
            WHERE user_id = @user_id
              AND env = @env
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("role", "STRING", role),
                    bigquery.ScalarQueryParameter("lawyer_status", "STRING", lawyer_status),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            
            logger.info(f"Updated role for {user_id}: {role} ({lawyer_status})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user role: {e}")
            return False
    
    async def create_lawyer_application(self, application_data: Dict) -> Optional[str]:
        """
        Create lawyer verification application
        
        Args:
            application_data: Dict with lawyer application fields
            
        Returns:
            application_id if successful
        """
        if not self.client:
            logger.warning("BigQuery not available, skipping application creation")
            return str(uuid.uuid4())
        
        try:
            application_id = str(uuid.uuid4())
            
            query = f"""
            INSERT INTO `{self.project_id}.{self.dataset_id}.lawyer_applications`
            (
              application_id, user_id, full_name, email, phone_number,
              country, jurisdiction, bar_number, regulator_name, bar_admission_date,
              practice_areas, years_of_experience, firm_name, firm_address, website_url,
              bar_license_url, government_id_url, credentials_url,
              status, submitted_at, env
            )
            VALUES (
              @application_id, @user_id, @full_name, @email, @phone_number,
              @country, @jurisdiction, @bar_number, @regulator_name, @bar_admission_date,
              @practice_areas, @years_of_experience, @firm_name, @firm_address, @website_url,
              @bar_license_url, @government_id_url, @credentials_url,
              'pending', CURRENT_TIMESTAMP(), @env
            )
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("application_id", "STRING", application_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", application_data['user_id']),
                    bigquery.ScalarQueryParameter("full_name", "STRING", application_data['full_name']),
                    bigquery.ScalarQueryParameter("email", "STRING", application_data['email']),
                    bigquery.ScalarQueryParameter("phone_number", "STRING", application_data.get('phone_number')),
                    bigquery.ScalarQueryParameter("country", "STRING", application_data['country']),
                    bigquery.ScalarQueryParameter("jurisdiction", "STRING", application_data['jurisdiction']),
                    bigquery.ScalarQueryParameter("bar_number", "STRING", application_data['bar_number']),
                    bigquery.ScalarQueryParameter("regulator_name", "STRING", application_data['regulator_name']),
                    bigquery.ScalarQueryParameter("bar_admission_date", "DATE", application_data.get('bar_admission_date')),
                    bigquery.ArrayQueryParameter("practice_areas", "STRING", application_data.get('practice_areas', [])),
                    bigquery.ScalarQueryParameter("years_of_experience", "INT64", application_data.get('years_of_experience')),
                    bigquery.ScalarQueryParameter("firm_name", "STRING", application_data.get('firm_name')),
                    bigquery.ScalarQueryParameter("firm_address", "STRING", application_data.get('firm_address')),
                    bigquery.ScalarQueryParameter("website_url", "STRING", application_data.get('website_url')),
                    bigquery.ScalarQueryParameter("bar_license_url", "STRING", application_data['bar_license_url']),
                    bigquery.ScalarQueryParameter("government_id_url", "STRING", application_data.get('government_id_url')),
                    bigquery.ScalarQueryParameter("credentials_url", "STRING", application_data.get('credentials_url')),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            
            logger.info(f"Created lawyer application: {application_id}")
            return application_id
            
        except Exception as e:
            logger.error(f"Failed to create lawyer application: {e}")
            return None
    
    async def log_login_event(
        self,
        user_id: str,
        auth_provider: str,
        event_type: str,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> bool:
        """Log login/logout event"""
        if not self.client:
            return False
        
        try:
            event_id = str(uuid.uuid4())
            
            query = f"""
            INSERT INTO `{self.project_id}.{self.dataset_id}.login_events`
            (event_id, user_id, auth_provider, event_type, ip_address, user_agent,
             success, failure_reason, timestamp, env)
            VALUES
            (@event_id, @user_id, @auth_provider, @event_type, @ip_address, @user_agent,
             @success, @failure_reason, CURRENT_TIMESTAMP(), @env)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("event_id", "STRING", event_id),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("auth_provider", "STRING", auth_provider),
                    bigquery.ScalarQueryParameter("event_type", "STRING", event_type),
                    bigquery.ScalarQueryParameter("ip_address", "STRING", ip_address),
                    bigquery.ScalarQueryParameter("user_agent", "STRING", user_agent),
                    bigquery.ScalarQueryParameter("success", "BOOL", success),
                    bigquery.ScalarQueryParameter("failure_reason", "STRING", failure_reason),
                    bigquery.ScalarQueryParameter("env", "STRING", self.env),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log login event: {e}")
            return False


# Global instance
_bq_client = None

def get_bigquery_client() -> BigQueryIdentityClient:
    """Get BigQuery client instance"""
    global _bq_client
    if _bq_client is None:
        _bq_client = BigQueryIdentityClient()
    return _bq_client
