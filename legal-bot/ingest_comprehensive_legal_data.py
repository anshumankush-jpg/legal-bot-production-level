"""Ingest comprehensive legal dataset into backend."""
import requests
import json
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"
DATA_DIR = Path("collected_legal_data")


def ingest_legal_item(item: Dict, category: str) -> bool:
    """Ingest a single legal item into Artillery backend."""
    try:
        # Create a text file content
        content = f"""{item.get('title', 'Legal Document')}

{item.get('content', '')}

Jurisdiction: {item.get('jurisdiction', 'Unknown')}
Country: {item.get('country', 'Unknown')}
Category: {item.get('category', 'legal')}
Tags: {', '.join(item.get('tags', []))}
"""
        
        if 'case_reference' in item:
            content += f"\nCase Reference: {item.get('case_reference', 'N/A')}\n"
            content += f"Court: {item.get('court', 'N/A')}\n"
        
        # Upload as text file
        import tempfile
        import os
        
        filename = f"{category}_{item.get('title', 'document')[:50]}.txt"
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            with open(tmp_path, 'rb') as f:
                files = {'file': (filename, f, 'text/plain')}
                data = {
                    'user_id': 'system',
                    'offence_number': None
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/artillery/upload",
                    files=files,
                    data=data,
                    timeout=120
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Ingested: {filename} ({result.get('chunks_indexed', 0)} chunks)")
                return True
            else:
                logger.error(f"✗ Failed: {filename} - {response.status_code}")
                return False
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"✗ Error ingesting {item.get('title', 'item')}: {e}")
        return False


def load_and_ingest_dataset():
    """Load and ingest all collected legal data."""
    print("=" * 80)
    print("INGESTING COMPREHENSIVE LEGAL DATASET INTO BACKEND")
    print("=" * 80)
    
    # Check backend
    try:
        response = requests.get(f"{API_BASE_URL}/api/artillery/health", timeout=5)
        if response.status_code != 200:
            logger.error("Backend is not healthy")
            return False
    except Exception as e:
        logger.error(f"Backend is not running: {e}")
        return False
    
    # Load complete dataset
    dataset_file = DATA_DIR / "complete_legal_dataset.json"
    if not dataset_file.exists():
        logger.error(f"Dataset file not found: {dataset_file}")
        logger.info("Run comprehensive_legal_data_collector.py first")
        return False
    
    with open(dataset_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    total_ingested = 0
    total_failed = 0
    
    # Ingest each category
    for category, items in dataset.items():
        if not items:
            continue
        
        logger.info(f"\nIngesting {category} ({len(items)} items)...")
        for item in items:
            if ingest_legal_item(item, category):
                total_ingested += 1
            else:
                total_failed += 1
            time.sleep(0.5)  # Small delay to avoid overwhelming
    
    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print(f"Successfully ingested: {total_ingested} items")
    print(f"Failed: {total_failed} items")
    print("\nThe backend now has comprehensive legal data!")
    print("=" * 80)
    
    return total_ingested > 0


if __name__ == "__main__":
    success = load_and_ingest_dataset()
    sys.exit(0 if success else 1)
