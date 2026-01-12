"""
Process, chunk, and ingest all Canada and USA legal datasets into the vector database.
This script handles:
1. Loading legal datasets (Canada & USA laws)
2. Chunking documents for optimal retrieval
3. Generating embeddings using Sentence Transformers
4. Storing in FAISS vector database
5. Making data available to the chatbot
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
BATCH_SIZE = 10  # Process in batches to avoid overwhelming the API

class LegalDatasetProcessor:
    """Process and ingest legal datasets into the vector database."""
    
    def __init__(self, api_base_url: str = API_BASE_URL):
        self.api_base_url = api_base_url
        self.stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'successful_ingestions': 0,
            'failed_ingestions': 0,
            'start_time': None,
            'end_time': None
        }
    
    def check_backend_health(self) -> bool:
        """Check if backend is running and healthy."""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("[OK] Backend is healthy and running")
                return True
            else:
                logger.error(f"[FAIL] Backend returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"[FAIL] Backend is not accessible: {e}")
            return False
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
        
        Returns:
            List of text chunks
        """
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Get chunk
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - overlap if end < len(text) else end
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def create_document_content(self, item: Dict[str, Any], category: str) -> str:
        """Create formatted document content from legal item."""
        content_parts = [
            f"Title: {item.get('title', 'Legal Document')}",
            f"Category: {category}",
            f"Jurisdiction: {item.get('jurisdiction', 'Unknown')}",
            f"Country: {item.get('country', 'Unknown')}",
            ""
        ]
        
        # Add tags if available
        if 'tags' in item and item['tags']:
            content_parts.append(f"Tags: {', '.join(item['tags'])}")
            content_parts.append("")
        
        # Add case-specific information
        if 'case_reference' in item:
            content_parts.extend([
                f"Case Reference: {item.get('case_reference', 'N/A')}",
                f"Court: {item.get('court', 'N/A')}",
                f"Year: {item.get('year', 'N/A')}",
                ""
            ])
        
        # Add main content
        content_parts.append("Content:")
        content_parts.append(item.get('content', ''))
        
        return "\n".join(content_parts)
    
    def ingest_document_via_api(self, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Ingest a document into the backend via the upload API.
        
        Args:
            content: Document content
            metadata: Document metadata
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a temporary text file with the content
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            try:
                # Upload via API
                with open(tmp_path, 'rb') as f:
                    files = {'file': (metadata.get('filename', 'document.txt'), f, 'text/plain')}
                    data = {
                        'user_id': 'system_legal_db',
                        'offence_number': metadata.get('offence_number', '')
                    }
                    
                    response = requests.post(
                        f"{self.api_base_url}/api/artillery/upload",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"[OK] Ingested: {metadata.get('title', 'document')[:50]}... ({result.get('chunks_indexed', 0)} chunks)")
                        return True
                    else:
                        logger.error(f"[FAIL] Failed to ingest {metadata.get('title', 'document')[:50]}: {response.status_code} - {response.text[:200]}")
                        return False
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        except Exception as e:
            logger.error(f"[ERROR] Error ingesting document: {e}")
            return False
    
    def process_dataset_file(self, file_path: Path, category: str) -> Dict[str, int]:
        """
        Process a single dataset file.
        
        Args:
            file_path: Path to JSON dataset file
            category: Category name (e.g., 'criminal', 'traffic')
        
        Returns:
            Statistics dictionary
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {file_path.name}")
        logger.info(f"Category: {category}")
        logger.info(f"{'='*80}\n")
        
        stats = {'processed': 0, 'successful': 0, 'failed': 0, 'chunks': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                # If it's a dict with categories as keys
                all_items = []
                for key, items in data.items():
                    if isinstance(items, list):
                        all_items.extend(items)
                    elif isinstance(items, dict):
                        all_items.append(items)
            elif isinstance(data, list):
                all_items = data
            else:
                logger.error(f"[ERROR] Unexpected data format in {file_path.name}")
                return stats
            
            logger.info(f"Found {len(all_items)} legal documents in {file_path.name}")
            
            # Process each item
            for idx, item in enumerate(all_items, 1):
                try:
                    stats['processed'] += 1
                    
                    # Create document content
                    full_content = self.create_document_content(item, category)
                    
                    # Chunk the content
                    chunks = self.chunk_text(full_content)
                    stats['chunks'] += len(chunks)
                    
                    logger.info(f"[{idx}/{len(all_items)}] Processing: {item.get('title', 'Unknown')[:60]}... ({len(chunks)} chunks)")
                    
                    # Create metadata
                    metadata = {
                        'title': item.get('title', 'Legal Document'),
                        'category': category,
                        'jurisdiction': item.get('jurisdiction', 'Unknown'),
                        'country': item.get('country', 'Unknown'),
                        'filename': f"{category}_{item.get('title', 'doc')[:30].replace(' ', '_')}.txt",
                        'tags': ', '.join(item.get('tags', [])),
                        'offence_number': item.get('offence_number', '')
                    }
                    
                    # Ingest document (backend will handle chunking internally)
                    if self.ingest_document_via_api(full_content, metadata):
                        stats['successful'] += 1
                    else:
                        stats['failed'] += 1
                    
                    # Small delay to avoid overwhelming the API
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"[ERROR] Error processing item {idx}: {e}")
                    stats['failed'] += 1
                    continue
            
            logger.info(f"\n[OK] Completed {file_path.name}: {stats['successful']}/{stats['processed']} successful, {stats['chunks']} total chunks")
            
        except Exception as e:
            logger.error(f"[ERROR] Error processing file {file_path.name}: {e}")
        
        return stats
    
    def process_all_datasets(self):
        """Process all available legal datasets."""
        self.stats['start_time'] = datetime.now()
        
        logger.info("\n" + "="*80)
        logger.info("🚀 STARTING LEGAL DATASET INGESTION")
        logger.info("="*80 + "\n")
        
        # Check backend health
        if not self.check_backend_health():
            logger.error("[FAIL] Backend is not running. Please start the backend first:")
            logger.error("   cd backend")
            logger.error("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
            return
        
        # Define datasets to process
        datasets = [
            # Complete comprehensive dataset
            {
                'path': Path('collected_legal_data/complete_legal_dataset.json'),
                'category': 'comprehensive_legal'
            },
            # Individual datasets
            {
                'path': Path('collected_legal_data/usa_federal_criminal.json'),
                'category': 'usa_federal_criminal'
            },
            {
                'path': Path('collected_legal_data/canada_federal_criminal.json'),
                'category': 'canada_federal_criminal'
            },
            {
                'path': Path('collected_legal_data/usa_traffic_laws.json'),
                'category': 'usa_traffic_laws'
            },
            {
                'path': Path('collected_legal_data/case_studies.json'),
                'category': 'case_studies'
            },
            {
                'path': Path('all_laws_database/all_laws.json'),
                'category': 'all_laws_database'
            }
        ]
        
        # Process each dataset
        for dataset_info in datasets:
            file_path = dataset_info['path']
            
            if not file_path.exists():
                logger.warning(f"[WARN] Dataset not found: {file_path}")
                continue
            
            stats = self.process_dataset_file(file_path, dataset_info['category'])
            
            # Update overall stats
            self.stats['total_documents'] += stats['processed']
            self.stats['total_chunks'] += stats['chunks']
            self.stats['successful_ingestions'] += stats['successful']
            self.stats['failed_ingestions'] += stats['failed']
        
        self.stats['end_time'] = datetime.now()
        self.print_final_report()
    
    def print_final_report(self):
        """Print final ingestion report."""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        logger.info("\n" + "="*80)
        logger.info("INGESTION COMPLETE - FINAL REPORT")
        logger.info("="*80)
        logger.info(f"Total Documents Processed: {self.stats['total_documents']}")
        logger.info(f"Total Chunks Created: {self.stats['total_chunks']}")
        logger.info(f"Successful Ingestions: {self.stats['successful_ingestions']}")
        logger.info(f"Failed Ingestions: {self.stats['failed_ingestions']}")
        logger.info(f"Success Rate: {(self.stats['successful_ingestions'] / max(self.stats['total_documents'], 1) * 100):.1f}%")
        logger.info(f"Total Time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        logger.info(f"Average Time per Document: {(duration / max(self.stats['total_documents'], 1)):.2f} seconds")
        logger.info("="*80)
        
        # Test the system
        logger.info("\nTesting the ingested data...")
        self.test_retrieval()
    
    def test_retrieval(self):
        """Test if documents can be retrieved from the vector database."""
        test_queries = [
            "What are the penalties for speeding in Ontario?",
            "What is the federal criminal code for conspiracy?",
            "What are the penalties for DUI in California?",
            "What is the Canadian Charter of Rights?",
            "What are the truck driver cargo securement rules?"
        ]
        
        logger.info("\n" + "="*80)
        logger.info("TESTING VECTOR SEARCH")
        logger.info("="*80 + "\n")
        
        for query in test_queries:
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/artillery/chat",
                    json={'message': query, 'top_k': 5},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"[OK] Query: {query}")
                    logger.info(f"   Chunks used: {result.get('chunks_used', 0)}")
                    logger.info(f"   Answer preview: {result.get('answer', '')[:100]}...")
                else:
                    logger.error(f"[FAIL] Query failed: {query} - Status: {response.status_code}")
            except Exception as e:
                logger.error(f"[ERROR] Error testing query '{query}': {e}")
            
            time.sleep(1)  # Small delay between tests


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("LEGAL DATASET PROCESSOR & INGESTION SYSTEM")
    print("="*80)
    print("\nThis script will:")
    print("1. Load all Canada & USA legal datasets")
    print("2. Chunk documents for optimal retrieval")
    print("3. Generate embeddings using Sentence Transformers")
    print("4. Store in FAISS vector database")
    print("5. Make data available to the chatbot")
    print("\n" + "="*80 + "\n")
    
    # Confirm backend is running
    print("IMPORTANT: Make sure the backend server is running!")
    print("   If not, run: cd backend && python -m uvicorn app.main:app --reload\n")
    
    response = input("Continue with ingestion? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Ingestion cancelled.")
        return
    
    # Create processor and run
    processor = LegalDatasetProcessor()
    processor.process_all_datasets()
    
    print("\nAll done! Your legal chatbot is now ready to answer questions.")
    print("   Test it at: http://localhost:4200")
    print("   Or via API: http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
