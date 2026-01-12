"""Ingest all legal documents to Pinecone - Non-interactive version."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from pathlib import Path
from typing import List, Dict, Any
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_all_documents(base_dir: Path) -> List[Path]:
    """Find all legal documents in the project."""
    search_dirs = [
        "canada criminal and federal law",
        "CANADA TRAFFIC FILES",
        "canada_case_law",
        "canada_criminal_law",
        "canada_traffic_acts",
        "us_state_codes",
        "us_traffic_laws",
        "USA",
        "usa_case_law",
        "usa_criminal_law",
        "data/downloaded_pdfs",
        "enhanced_legal_text"
    ]
    
    supported_extensions = {'.pdf', '.txt', '.html', '.htm', '.md'}
    documents = []
    
    for search_dir in search_dirs:
        dir_path = base_dir / search_dir
        if dir_path.exists():
            logger.info(f"Scanning: {search_dir}")
            for file_path in dir_path.rglob('*'):
                if file_path.suffix.lower() in supported_extensions:
                    if file_path.stat().st_size > 0:  # Skip empty files
                        documents.append(file_path)
    
    return documents


def ingest_documents_to_pinecone():
    """Main ingestion function."""
    print("="*80)
    print("INGESTING DOCUMENTS TO PINECONE")
    print("="*80)
    print()
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    
    # Import backend services
    try:
        from app.core.config import settings
        from app.vector_store import get_vector_store
        from app.embeddings.embedding_service import EmbeddingService
        import fitz  # PyMuPDF
        from bs4 import BeautifulSoup
        
        logger.info("[OK] Backend modules imported")
    except Exception as e:
        logger.error(f"[ERROR] Failed to import backend modules: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check configuration
    print(f"\n[CONFIG] Vector Store: {settings.VECTOR_STORE}")
    print(f"[CONFIG] Pinecone Index: {settings.PINECONE_INDEX_NAME}")
    print(f"[CONFIG] Embedding Provider: {settings.EMBEDDING_PROVIDER}")
    print(f"[CONFIG] Embedding Dimension: {settings.EMBEDDING_DIMENSIONS}")
    
    if settings.VECTOR_STORE != "pinecone":
        print(f"\n[WARNING] VECTOR_STORE is set to '{settings.VECTOR_STORE}', not 'pinecone'")
        print("[INFO] This will still work, but make sure Pinecone is configured correctly")
    
    # Initialize services
    print("\n[1/5] Initializing services...")
    try:
        vector_store = get_vector_store()
        embedding_service = EmbeddingService()
        
        print(f"[OK] Services initialized")
        print(f"     Vector Store: {type(vector_store).__name__}")
        print(f"     Embedding Service: {type(embedding_service).__name__}")
        
        # Get current stats
        stats = vector_store.get_stats()
        print(f"     Current vectors: {stats.get('total_vectors', 0)}")
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize services: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Find documents
    print("\n[2/5] Finding documents...")
    documents = find_all_documents(base_dir)
    
    print(f"[OK] Found {len(documents)} documents")
    
    # Count by type
    by_type = {}
    for doc in documents:
        ext = doc.suffix.lower()
        by_type[ext] = by_type.get(ext, 0) + 1
    
    for ext, count in sorted(by_type.items()):
        print(f"     {ext}: {count} files")
    
    if not documents:
        print("\n[WARNING] No documents found!")
        return False
    
    # Process documents
    print(f"\n[3/5] Processing and embedding documents...")
    print(f"[INFO] This will take ~10-20 minutes for {len(documents)} documents")
    print(f"[INFO] Estimated cost: ~$1-2 (OpenAI embeddings)")
    print()
    
    processed = 0
    failed = 0
    skipped = 0
    
    batch_embeddings = []
    batch_metadatas = []
    batch_size = 50  # Process in batches
    
    start_time = time.time()
    
    for idx, doc_path in enumerate(documents, 1):
        try:
            # Show progress
            if idx % 10 == 0 or idx == 1:
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                remaining = (len(documents) - idx) / rate if rate > 0 else 0
                print(f"[{idx}/{len(documents)}] Processing... "
                      f"(~{remaining/60:.1f} min remaining, "
                      f"{processed} done, {failed} failed)")
            
            # Extract text
            try:
                if doc_path.suffix.lower() == '.pdf':
                    # Extract text from PDF using PyMuPDF
                    try:
                        pdf_document = fitz.open(str(doc_path))
                        text = ""
                        for page in pdf_document:
                            text += page.get_text()
                        pdf_document.close()
                    except Exception as pdf_error:
                        logger.warning(f"PDF extraction failed for {doc_path.name}: {pdf_error}")
                        failed += 1
                        continue
                        
                elif doc_path.suffix.lower() in ['.html', '.htm']:
                    # Read HTML and strip tags
                    html_content = doc_path.read_text(encoding='utf-8', errors='ignore')
                    soup = BeautifulSoup(html_content, 'html.parser')
                    text = soup.get_text(separator='\n')
                else:
                    text = doc_path.read_text(encoding='utf-8', errors='ignore')
                
                if not text or len(text.strip()) < 50:
                    skipped += 1
                    continue
                
                # Truncate if too long (to avoid token limits)
                if len(text) > 50000:
                    text = text[:50000]
                
            except Exception as e:
                logger.warning(f"Failed to extract text from {doc_path.name}: {e}")
                failed += 1
                continue
            
            # Generate embedding
            try:
                embedding = embedding_service.embed_text(text[:8000])  # Limit for embedding
                
                # Handle different return formats
                if hasattr(embedding, 'tolist'):
                    # Convert numpy array to list
                    embedding = embedding.tolist()
                
                # Flatten if nested list
                while isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], (list, tuple)):
                    embedding = embedding[0]
                
                # Ensure it's a flat list of floats
                if not isinstance(embedding, list):
                    raise ValueError(f"Embedding is not a list: {type(embedding)}")
                
                embedding = [float(x) if not isinstance(x, (list, tuple)) else float(x[0]) for x in embedding]
                
                # Prepare metadata
                metadata = {
                    'filename': doc_path.name,
                    'filepath': str(doc_path.relative_to(base_dir)),
                    'text': text[:1000],  # Store first 1000 chars
                    'file_type': doc_path.suffix.lower(),
                }
                
                # Try to infer jurisdiction
                text_lower = text.lower()
                if 'ontario' in text_lower:
                    metadata['jurisdiction'] = 'Ontario'
                elif 'alberta' in text_lower:
                    metadata['jurisdiction'] = 'Alberta'
                elif 'british columbia' in text_lower or 'bc' in doc_path.name.lower():
                    metadata['jurisdiction'] = 'BC'
                elif 'california' in text_lower:
                    metadata['jurisdiction'] = 'California'
                
                batch_embeddings.append(embedding)
                batch_metadatas.append(metadata)
                processed += 1
                
                # Upload batch when full
                if len(batch_embeddings) >= batch_size:
                    vector_store.add_documents(batch_embeddings, batch_metadatas)
                    logger.info(f"[UPLOADED] Batch of {len(batch_embeddings)} documents")
                    batch_embeddings = []
                    batch_metadatas = []
                    time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Failed to embed {doc_path.name}: {e}")
                failed += 1
                continue
                
        except Exception as e:
            logger.error(f"Error processing {doc_path.name}: {e}")
            failed += 1
            continue
    
    # Upload remaining batch
    if batch_embeddings:
        vector_store.add_documents(batch_embeddings, batch_metadatas)
        logger.info(f"[UPLOADED] Final batch of {len(batch_embeddings)} documents")
    
    # Final stats
    print("\n[4/5] Getting final statistics...")
    final_stats = vector_store.get_stats()
    
    print("\n[5/5] Ingestion complete!")
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total documents found: {len(documents)}")
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")
    print(f"Skipped (too small): {skipped}")
    print(f"\nFinal vector count: {final_stats.get('total_vectors', 'N/A')}")
    print(f"Index dimension: {final_stats.get('dimension', 'N/A')}")
    
    elapsed_time = time.time() - start_time
    print(f"\nTime taken: {elapsed_time/60:.1f} minutes")
    print("="*80)
    
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PINECONE DOCUMENT INGESTION")
    print("="*80)
    print("\nThis will:")
    print("1. Find all legal documents in your project")
    print("2. Extract text from PDFs, HTML, and text files")
    print("3. Generate embeddings using OpenAI")
    print("4. Upload to Pinecone cloud")
    print("\nEstimated time: 10-20 minutes")
    print("Estimated cost: $1-2 (OpenAI embeddings)")
    print("="*80)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    try:
        success = ingest_documents_to_pinecone()
        if success:
            print("\n[SUCCESS] All documents ingested to Pinecone!")
            print("\nNext steps:")
            print("1. Restart your backend: python -m uvicorn app.main:app --reload")
            print("2. Test queries: python test_backend_question.py")
            sys.exit(0)
        else:
            print("\n[FAILED] Ingestion failed. Check errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Ingestion cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
