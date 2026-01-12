"""Comprehensive Legal Document Ingestion for Artillery Backend."""
import requests
import json
import sys
import time
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"

# Define all folders containing legal documents
LEGAL_DOCUMENT_FOLDERS = [
    ("canada_traffic_acts", "Canada Traffic Law"),
    ("canada_criminal_law", "Canada Criminal Law"),
    ("canada_case_law", "Canada Case Law"),
    ("usa_criminal_law", "USA Criminal Law"),
    ("usa_case_law", "USA Case Law"),
    ("us_traffic_laws", "USA Traffic Law"),
]

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.html', '.txt', '.json'}

def upload_file_to_backend(file_path: Path, category: str) -> bool:
    """Upload a single file to the Artillery backend."""
    try:
        # Determine file metadata
        filename = file_path.name
        logger.info(f"Processing: {filename} ({category})")
        
        # Skip if file is too small or empty
        if file_path.stat().st_size < 100:
            logger.warning(f"Skipping (too small): {filename}")
            return False
        
        # Upload to backend
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
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
            chunks = result.get('chunks_indexed', 0)
            logger.info(f"✓ SUCCESS: {filename} ({chunks} chunks indexed)")
            return True
        else:
            logger.error(f"✗ FAILED: {filename} - Status {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        logger.error(f"✗ ERROR: {filename} - {str(e)}")
        return False

def ingest_folder(folder_name: str, category: str, base_dir: Path) -> dict:
    """Ingest all documents from a folder."""
    folder_path = base_dir / folder_name
    
    if not folder_path.exists():
        logger.warning(f"Folder not found: {folder_path}")
        return {"processed": 0, "successful": 0, "failed": 0}
    
    logger.info(f"\n{'='*80}")
    logger.info(f"PROCESSING FOLDER: {folder_name} ({category})")
    logger.info(f"{'='*80}")
    
    stats = {"processed": 0, "successful": 0, "failed": 0}
    
    # Get all files in folder
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            stats["processed"] += 1
            
            success = upload_file_to_backend(file_path, category)
            if success:
                stats["successful"] += 1
            else:
                stats["failed"] += 1
            
            # Small delay to avoid overwhelming the backend
            time.sleep(0.5)
    
    logger.info(f"\nFolder Summary: {stats['successful']}/{stats['processed']} successful\n")
    return stats

def main():
    """Main ingestion function."""
    print("\n" + "="*80)
    print("COMPREHENSIVE LEGAL DOCUMENT INGESTION")
    print("="*80 + "\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/artillery/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            logger.info(f"✓ Backend is healthy")
            logger.info(f"  Current index size: {health.get('faiss_index_size', 0)} documents")
        else:
            logger.error("✗ Backend is not healthy")
            sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Backend is not running: {e}")
        logger.info("\nTo start backend:")
        logger.info("  cd backend")
        logger.info("  python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    base_dir = Path(__file__).parent
    total_stats = {"processed": 0, "successful": 0, "failed": 0}
    
    # Process each folder
    for folder_name, category in LEGAL_DOCUMENT_FOLDERS:
        folder_stats = ingest_folder(folder_name, category, base_dir)
        
        total_stats["processed"] += folder_stats["processed"]
        total_stats["successful"] += folder_stats["successful"]
        total_stats["failed"] += folder_stats["failed"]
    
    # Also upload the PDF files in the root directory
    logger.info(f"\n{'='*80}")
    logger.info("PROCESSING ROOT DIRECTORY PDFs")
    logger.info(f"{'='*80}")
    
    for pdf_file in base_dir.glob("*.pdf"):
        if pdf_file.name in ["ALEBRTA RUL BOOK.pdf", "ONTARIO LAW SUITS .pdf"]:
            total_stats["processed"] += 1
            success = upload_file_to_backend(pdf_file, "Legal Document")
            if success:
                total_stats["successful"] += 1
            else:
                total_stats["failed"] += 1
            time.sleep(0.5)
    
    # Final summary
    print("\n" + "="*80)
    print("INGESTION COMPLETE")
    print("="*80)
    print(f"Total Processed: {total_stats['processed']}")
    print(f"Successful: {total_stats['successful']}")
    print(f"Failed: {total_stats['failed']}")
    print(f"Success Rate: {(total_stats['successful']/total_stats['processed']*100) if total_stats['processed'] > 0 else 0:.1f}%")
    
    # Check final index size
    try:
        response = requests.get(f"{API_BASE_URL}/api/artillery/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"\nFinal Index Size: {health.get('faiss_index_size', 0)} document chunks")
    except:
        pass
    
    print("="*80 + "\n")
    
    if total_stats['successful'] > 0:
        logger.info("✓ Ready to answer questions!")
        logger.info("\nTest with:")
        logger.info("  python test_backend_question.py")
    else:
        logger.warning("⚠ No documents were successfully ingested")

if __name__ == "__main__":
    main()
