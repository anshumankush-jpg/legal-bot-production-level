"""Ingest all comprehensive laws into Artillery backend."""
import requests
import json
import sys
import time
import logging
from pathlib import Path
import tempfile
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"
DATA_DIR = Path("collected_legal_data")

def ingest_legal_item(item: dict, category: str) -> bool:
    """Ingest a single legal item into Artillery backend."""
    try:
        # Create content
        content = f"""{item.get('title', 'Legal Document')}

{item.get('content', '')}

Jurisdiction: {item.get('jurisdiction', 'Unknown')}
Country: {item.get('country', 'Unknown')}
Category: {item.get('category', category)}
Tags: {', '.join(item.get('tags', []))}
"""
        
        if 'case_reference' in item:
            content += f"\nCase Reference: {item.get('case_reference', 'N/A')}\n"
            content += f"Court: {item.get('court', 'N/A')}\n"
        
        # Create filename
        filename = f"{category}_{item.get('title', 'document')[:50]}.txt"
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Upload to backend
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

def main():
    """Main ingestion function."""
    print("=" * 80)
    print("INGESTING ALL LAWS INTO BACKEND")
    print("=" * 80)
    
    # Check backend
    try:
        response = requests.get(f"{API_BASE_URL}/api/artillery/health", timeout=5)
        if response.status_code != 200:
            logger.error("Backend is not healthy")
            return False
    except Exception as e:
        logger.error(f"Backend is not running: {e}")
        logger.info("Start backend with: cd backend && python -m uvicorn app.main:app --reload")
        return False
    
    # Load dataset
    dataset_file = DATA_DIR / "complete_legal_dataset.json"
    if not dataset_file.exists():
        logger.error(f"Dataset not found: {dataset_file}")
        logger.info("Run create_all_laws_dataset.py first")
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
            time.sleep(0.3)  # Small delay
    
    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print(f"Successfully ingested: {total_ingested} items")
    print(f"Failed: {total_failed} items")
    print("\nThe backend now has comprehensive legal data covering:")
    print("- Criminal law")
    print("- Traffic law")
    print("- Divorce law")
    print("- Copyright & content owner rules")
    print("- Commercial vehicle regulations")
    print("- Civil law")
    print("- Constitutional law")
    print("- And more!")
    print("=" * 80)
    
    return total_ingested > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
