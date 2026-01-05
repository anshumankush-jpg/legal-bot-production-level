"""Azure Blob Storage integration for document storage."""
import logging
from typing import Optional
from pathlib import Path
import tempfile

try:
    from azure.storage.blob import BlobServiceClient, BlobClient
    from azure.identity import DefaultAzureCredential
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Azure Storage SDK not installed. Install with: pip install azure-storage-blob")

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureBlobStorageClient:
    """Client for Azure Blob Storage operations."""
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_name: Optional[str] = None,
        container_name: Optional[str] = None
    ):
        """
        Initialize Azure Blob Storage client.
        
        Args:
            connection_string: Azure Storage connection string
            account_name: Storage account name (if using managed identity)
            container_name: Container name
        """
        if not AZURE_STORAGE_AVAILABLE:
            raise RuntimeError("Azure Storage SDK not installed")
        
        self.container_name = container_name or settings.AZURE_STORAGE_CONTAINER
        
        if connection_string or settings.AZURE_STORAGE_CONNECTION_STRING:
            self.blob_service = BlobServiceClient.from_connection_string(
                connection_string or settings.AZURE_STORAGE_CONNECTION_STRING
            )
        elif account_name or settings.AZURE_STORAGE_ACCOUNT:
            account = account_name or settings.AZURE_STORAGE_ACCOUNT
            credential = DefaultAzureCredential()
            self.blob_service = BlobServiceClient(
                account_url=f"https://{account}.blob.core.windows.net",
                credential=credential
            )
        else:
            raise ValueError("Either connection_string or account_name must be provided")
    
    def download_blob(self, blob_name: str, destination_path: Optional[str] = None) -> str:
        """
        Download a blob to a local file.
        
        Args:
            blob_name: Name of the blob
            destination_path: Optional destination path (creates temp file if not provided)
            
        Returns:
            Path to downloaded file
        """
        if destination_path is None:
            # Create temp file
            suffix = Path(blob_name).suffix
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            destination_path = temp_file.name
            temp_file.close()
        
        blob_client = self.blob_service.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )
        
        with open(destination_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        logger.info(f"Downloaded {blob_name} to {destination_path}")
        return destination_path
    
    def upload_blob(self, file_path: str, blob_name: Optional[str] = None) -> str:
        """
        Upload a file to blob storage.
        
        Args:
            file_path: Path to local file
            blob_name: Optional blob name (uses filename if not provided)
            
        Returns:
            Blob name
        """
        if blob_name is None:
            blob_name = Path(file_path).name
        
        blob_client = self.blob_service.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"Uploaded {file_path} as {blob_name}")
        return blob_name


# Global singleton instance
_blob_client: Optional[AzureBlobStorageClient] = None


def get_blob_client() -> Optional[AzureBlobStorageClient]:
    """Get or create the global blob storage client instance."""
    global _blob_client
    if settings.USE_AZURE_STORAGE and (_blob_client is None):
        try:
            _blob_client = AzureBlobStorageClient()
        except Exception as e:
            logger.warning(f"Could not initialize blob storage client: {e}")
            return None
    return _blob_client


def download_pdf_from_blob(blob_name: str) -> str:
    """
    Download a PDF from Azure Blob Storage.
    
    Args:
        blob_name: Name of the blob
        
    Returns:
        Path to downloaded file
    """
    client = get_blob_client()
    if client is None:
        raise RuntimeError("Azure Blob Storage not configured")
    return client.download_blob(blob_name)

