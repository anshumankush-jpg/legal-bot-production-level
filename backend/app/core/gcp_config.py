"""GCP-specific configuration and utilities."""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# GCP Environment detection
def is_gcp_environment() -> bool:
    """Check if running in GCP environment."""
    return (
        os.getenv("GOOGLE_CLOUD_PROJECT") is not None or
        os.getenv("GCP_PROJECT") is not None or
        os.getenv("GAE_ENV") is not None or
        os.path.exists("/sys/class/dmi/id/product_name")  # GCP VMs
    )


def get_gcp_project_id() -> Optional[str]:
    """Get GCP project ID from environment."""
    return os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")


# For GCP deployment, we can use:
# - Cloud Storage for document storage (instead of local files)
# - Firestore for matters storage (instead of JSON files)
# - Cloud Secret Manager for API keys
# - Cloud Run or GKE for hosting

def get_storage_backend() -> str:
    """
    Determine storage backend based on environment.
    
    Returns:
        "gcp" if in GCP, "local" otherwise
    """
    if is_gcp_environment():
        return "gcp"
    return "local"


# GCP Storage integration (optional - can be implemented later)
try:
    from google.cloud import storage
    from google.cloud import firestore
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    logger.info("GCP libraries not installed. Install with: pip install google-cloud-storage google-cloud-firestore")


def get_gcp_storage_client():
    """Get GCP Cloud Storage client if available."""
    if GCP_AVAILABLE and is_gcp_environment():
        return storage.Client()
    return None


def get_gcp_firestore_client():
    """Get GCP Firestore client if available."""
    if GCP_AVAILABLE and is_gcp_environment():
        return firestore.Client()
    return None

