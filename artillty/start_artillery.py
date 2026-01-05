#!/usr/bin/env python3
"""
Artillery Embedding System Startup Script
Starts the Artillery API server with all components initialized
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_server import app
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Start the Artillery API server."""
    logger.info("🚀 Starting PLAZA-AI Artillery Embedding System")

    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"📍 Server configuration: {host}:{port} (debug={debug})")
    logger.info("📚 Artillery components initialized:")
    logger.info("   • SentenceTransformer (all-MiniLM-L6-v2)")
    logger.info("   • CLIP (ViT-B/32) with 384D projection")
    logger.info("   • FAISS IndexFlatIP vector store")
    logger.info("   • Multi-format document processor")
    logger.info("   • Legal domain specialized features")

    # Start server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )


if __name__ == "__main__":
    main()