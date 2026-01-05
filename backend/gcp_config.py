"""
GCP Configuration for PLAZA-AI
Handles Cloud Storage, Cloud SQL, and GCP service integration
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

# GCP imports (optional)
try:
    from google.cloud import storage
    from google.cloud import firestore
    from google.cloud import secretmanager
    import google.auth
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

logger = logging.getLogger(__name__)


class GCPConfig:
    """GCP configuration and service management."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        region: str = "us-central1",
        storage_bucket: Optional[str] = None,
        sql_instance: Optional[str] = None,
        sql_database: str = "plaza_ai"
    ):
        """
        Initialize GCP configuration.

        Args:
            project_id: GCP project ID
            region: GCP region
            storage_bucket: Cloud Storage bucket name
            sql_instance: Cloud SQL instance name
            sql_database: Cloud SQL database name
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
        self.region = region
        self.storage_bucket = storage_bucket or os.getenv("GCS_BUCKET_NAME")
        self.sql_instance = sql_instance or os.getenv("CLOUD_SQL_INSTANCE")
        self.sql_database = sql_database

        # Service clients (lazy initialization)
        self._storage_client = None
        self._firestore_client = None
        self._secret_client = None

        if GCP_AVAILABLE and self.project_id:
            logger.info(f"☁️ GCP configuration initialized for project: {self.project_id}")
        else:
            logger.warning("⚠️ GCP services not available or not configured")

    @property
    def is_gcp_environment(self) -> bool:
        """Check if running in GCP environment."""
        return (
            self.project_id is not None or
            os.getenv("GAE_ENV") is not None or
            os.path.exists("/sys/class/dmi/id/product_name")  # GCP VMs
        )

    @property
    def storage_client(self):
        """Get Cloud Storage client (lazy initialization)."""
        if not GCP_AVAILABLE:
            raise ImportError("GCP libraries not installed")

        if self._storage_client is None:
            self._storage_client = storage.Client(project=self.project_id)

        return self._storage_client

    @property
    def firestore_client(self):
        """Get Firestore client (lazy initialization)."""
        if not GCP_AVAILABLE:
            raise ImportError("GCP libraries not installed")

        if self._firestore_client is None:
            self._firestore_client = firestore.Client(project=self.project_id)

        return self._firestore_client

    @property
    def secret_client(self):
        """Get Secret Manager client (lazy initialization)."""
        if not GCP_AVAILABLE:
            raise ImportError("GCP libraries not installed")

        if self._secret_client is None:
            self._secret_client = secretmanager.SecretManagerServiceClient()

        return self._secret_client

    def get_secret(self, secret_name: str, version: str = "latest") -> str:
        """
        Retrieve secret from Google Secret Manager.

        Args:
            secret_name: Name of the secret
            version: Secret version

        Returns:
            Secret value as string
        """
        if not self.is_gcp_environment:
            # Try environment variable fallback
            env_name = secret_name.upper().replace("-", "_")
            return os.getenv(env_name, "")

        try:
            name = self.secret_client.secret_version_path(
                self.project_id, secret_name, version
            )
            response = self.secret_client.access_secret_version(name=name)
            return response.payload.data.decode("UTF-8")

        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise

    def upload_to_storage(
        self,
        local_path: str,
        storage_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to Cloud Storage.

        Args:
            local_path: Local file path
            storage_path: Path in storage bucket
            content_type: MIME content type

        Returns:
            Public URL of uploaded file
        """
        if not self.storage_bucket:
            raise ValueError("Storage bucket not configured")

        try:
            bucket = self.storage_client.bucket(self.storage_bucket)
            blob = bucket.blob(storage_path)

            # Set content type if provided
            if content_type:
                blob.content_type = content_type

            # Upload file
            blob.upload_from_filename(local_path)

            # Make publicly accessible
            blob.make_public()

            logger.info(f"☁️ Uploaded {local_path} to gs://{self.storage_bucket}/{storage_path}")
            return blob.public_url

        except Exception as e:
            logger.error(f"Failed to upload to storage: {e}")
            raise

    def download_from_storage(self, storage_path: str, local_path: str) -> bool:
        """
        Download file from Cloud Storage.

        Args:
            storage_path: Path in storage bucket
            local_path: Local destination path

        Returns:
            True if download successful
        """
        if not self.storage_bucket:
            raise ValueError("Storage bucket not configured")

        try:
            bucket = self.storage_client.bucket(self.storage_bucket)
            blob = bucket.blob(storage_path)

            # Ensure local directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            blob.download_to_filename(local_path)
            logger.info(f"☁️ Downloaded gs://{self.storage_bucket}/{storage_path} to {local_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download from storage: {e}")
            return False

    def list_storage_files(self, prefix: str = "") -> list:
        """
        List files in storage bucket.

        Args:
            prefix: File prefix to filter by

        Returns:
            List of file names
        """
        if not self.storage_bucket:
            raise ValueError("Storage bucket not configured")

        try:
            bucket = self.storage_client.bucket(self.storage_bucket)
            blobs = bucket.list_blobs(prefix=prefix)

            files = [blob.name for blob in blobs]
            logger.debug(f"📋 Listed {len(files)} files in storage")
            return files

        except Exception as e:
            logger.error(f"Failed to list storage files: {e}")
            return []

    def save_to_firestore(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """
        Save data to Firestore.

        Args:
            collection: Firestore collection name
            document_id: Document ID
            data: Data to save

        Returns:
            True if save successful
        """
        try:
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc_ref.set(data)
            logger.debug(f"💾 Saved to Firestore: {collection}/{document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save to Firestore: {e}")
            return False

    def load_from_firestore(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Load data from Firestore.

        Args:
            collection: Firestore collection name
            document_id: Document ID

        Returns:
            Document data or None if not found
        """
        try:
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to load from Firestore: {e}")
            return None

    @contextmanager
    def temporary_storage_download(self, storage_path: str):
        """
        Context manager for temporary download from storage.

        Usage:
            with gcp_config.temporary_storage_download("path/to/file.bin") as local_path:
                # Use local_path
                pass
        """
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            local_path = tmp_file.name

        try:
            success = self.download_from_storage(storage_path, local_path)
            if success:
                yield local_path
            else:
                yield None
        finally:
            if os.path.exists(local_path):
                os.unlink(local_path)

    def get_cloud_sql_connection_string(self) -> str:
        """
        Get Cloud SQL connection string.

        Returns:
            PostgreSQL connection string for Cloud SQL
        """
        if not self.sql_instance:
            raise ValueError("Cloud SQL instance not configured")

        # Cloud SQL connection string format
        connection_string = (
            f"postgresql://postgres@{self.region}.{self.project_id}:5432/{self.sql_database}"
            f"?host=/cloudsql/{self.project_id}:{self.region}:{self.sql_instance}"
        )

        return connection_string

    def get_environment_config(self) -> Dict[str, str]:
        """
        Get environment configuration for PLAZA-AI.

        Returns:
            Dictionary of environment variables
        """
        config = {
            "GOOGLE_CLOUD_PROJECT": self.project_id or "",
            "GCP_PROJECT": self.project_id or "",
            "GCP_REGION": self.region,
            "GCS_BUCKET_NAME": self.storage_bucket or "",
            "CLOUD_SQL_INSTANCE": self.sql_instance or "",
            "CLOUD_SQL_DATABASE": self.sql_database,
        }

        # Add secrets if available
        if self.is_gcp_environment:
            try:
                config["CLOUD_SQL_PASSWORD"] = self.get_secret("db-password")
            except Exception:
                logger.warning("Could not retrieve database password from Secret Manager")

        return config

    def setup_logging_for_gcp(self):
        """Configure logging for GCP (Cloud Logging)."""
        import google.cloud.logging
        from google.cloud.logging.handlers import CloudLoggingHandler

        # Initialize Cloud Logging
        client = google.cloud.logging.Client()
        handler = CloudLoggingHandler(client)

        # Configure Python logging
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

        logger.info("☁️ GCP Cloud Logging configured")


# Global GCP config instance
_gcp_config_instance = None

def get_gcp_config(
    project_id: Optional[str] = None,
    storage_bucket: Optional[str] = None
) -> GCPConfig:
    """Get or create global GCP config instance."""
    global _gcp_config_instance
    if _gcp_config_instance is None:
        _gcp_config_instance = GCPConfig(
            project_id=project_id,
            storage_bucket=storage_bucket
        )
    return _gcp_config_instance