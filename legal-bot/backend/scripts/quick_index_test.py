"""
Quick test to index the Oklahoma statutes HTML file.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.legal_retrieval import get_legal_retrieval_service, initialize_legal_index
from app.legal_retrieval import LegalRetrievalService

def test_indexing():
    """Test indexing the Oklahoma statutes."""

    # Initialize service
    service = LegalRetrievalService()

    # Check if index loads
    index_ready = service.load_legal_index()
    print(f"Index ready: {index_ready}")

    # Try to manually add some test data to simulate indexing
    # In a real scenario, this would be done by the full processor

    # For now, let's just test retrieval on empty index
    chunks = service.search_legal_index("Oklahoma speeding", k=5)
    print(f"Found {len(chunks)} chunks for 'Oklahoma speeding'")

    if chunks:
        print("Sample chunk:")
        print(f"  Text: {chunks[0].text[:200]}...")
        print(f"  Jurisdiction: {chunks[0].jurisdiction}")
        print(f"  Citation: {chunks[0].citation}")
    else:
        print("No chunks found - index is empty")

if __name__ == "__main__":
    test_indexing()