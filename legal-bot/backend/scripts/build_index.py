"""CLI script to rebuild FAISS index from existing documents."""
import argparse
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.vector_store.faiss_store import FaissVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def rebuild_index():
    """Rebuild FAISS index from metadata file."""
    metadata_path = Path(settings.FAISS_METADATA_PATH)
    index_path = Path(settings.FAISS_INDEX_PATH)
    
    if not metadata_path.exists():
        logger.error(f"Metadata file not found: {metadata_path}")
        return
    
    logger.info("Rebuilding FAISS index...")
    logger.info(f"Metadata file: {metadata_path}")
    logger.info(f"Index file: {index_path}")
    
    # This would require re-embedding all texts, which needs the original texts
    # For now, this is a placeholder
    logger.warning("Full index rebuild requires re-embedding all texts.")
    logger.warning("This script is a placeholder. Use the API to re-ingest documents if needed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild FAISS index")
    args = parser.parse_args()
    rebuild_index()

