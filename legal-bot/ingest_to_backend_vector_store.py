#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Document Ingestion for Backend Vector Store
Ingests all legal documents into the backend's Artillery vector store
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from tqdm import tqdm

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import backend Artillery components (the ones the backend actually uses)
from backend.artillery.embedding_service import get_artillery_embedding_service
from backend.artillery.document_processor import get_artillery_document_processor
from backend.artillery.vector_store import ArtilleryVectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Document directories to process
DOCUMENT_DIRECTORIES = [
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

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.html', '.htm', '.txt', '.docx', '.json', '.md'}

def find_all_documents(base_path: Path) -> List[Path]:
    """Find all supported documents in the project."""
    documents = []
    
    for doc_dir in DOCUMENT_DIRECTORIES:
        dir_path = base_path / doc_dir
        if dir_path.exists() and dir_path.is_dir():
            logger.info(f"Scanning directory: {doc_dir}")
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    documents.append(file_path)
    
    return documents

def extract_province_from_path(file_path: Path) -> str:
    """Extract province/state code from file path."""
    path_str = str(file_path).lower()
    
    # Canadian provinces
    provinces = {
        'ontario': 'ON', 'alberta': 'AB', 'british_columbia': 'BC', 'bc': 'BC',
        'quebec': 'QC', 'manitoba': 'MB', 'saskatchewan': 'SK',
        'nova_scotia': 'NS', 'new_brunswick': 'NB', 'newfoundland': 'NL',
        'pei': 'PE', 'prince_edward': 'PE', 'yukon': 'YT',
        'northwest': 'NT', 'nunavut': 'NU'
    }
    
    # US states
    states = {
        'california': 'CA', 'new_york': 'NY', 'texas': 'TX', 'florida': 'FL',
        'illinois': 'IL', 'pennsylvania': 'PA', 'ohio': 'OH', 'georgia': 'GA',
        'michigan': 'MI', 'north_carolina': 'NC', 'new_jersey': 'NJ',
        'virginia': 'VA', 'washington': 'WA', 'arizona': 'AZ', 'massachusetts': 'MA',
        'tennessee': 'TN', 'indiana': 'IN', 'missouri': 'MO', 'maryland': 'MD',
        'wisconsin': 'WI', 'colorado': 'CO', 'minnesota': 'MN', 'south_carolina': 'SC',
        'alabama': 'AL', 'louisiana': 'LA', 'kentucky': 'KY', 'oregon': 'OR',
        'oklahoma': 'OK', 'connecticut': 'CT', 'utah': 'UT', 'iowa': 'IA',
        'nevada': 'NV', 'arkansas': 'AR', 'mississippi': 'MS', 'kansas': 'KS',
        'new_mexico': 'NM', 'nebraska': 'NE', 'west_virginia': 'WV', 'idaho': 'ID',
        'hawaii': 'HI', 'new_hampshire': 'NH', 'maine': 'ME', 'montana': 'MT',
        'rhode_island': 'RI', 'delaware': 'DE', 'south_dakota': 'SD',
        'north_dakota': 'ND', 'alaska': 'AK', 'vermont': 'VT', 'wyoming': 'WY'
    }
    
    for key, code in {**provinces, **states}.items():
        if key in path_str:
            return code
    
    # Check if it's Canada or USA
    if 'canada' in path_str or 'canadian' in path_str:
        return 'CA'
    elif 'usa' in path_str or 'united_states' in path_str or 'us_' in path_str:
        return 'US'
    
    return 'UNKNOWN'

def extract_document_type(file_path: Path) -> str:
    """Extract document type from path."""
    path_str = str(file_path).lower()
    
    if 'traffic' in path_str or 'highway' in path_str or 'motor_vehicle' in path_str:
        return 'traffic'
    elif 'criminal' in path_str:
        return 'criminal'
    elif 'case_law' in path_str:
        return 'case_law'
    elif 'demerit' in path_str:
        return 'demerit_table'
    else:
        return 'general'

def process_document(
    file_path: Path,
    doc_processor,
    embedding_service,
    vector_store,
    user_id: str = "system"
) -> Dict[str, Any]:
    """Process a single document and add to vector store."""
    try:
        logger.info(f"Processing: {file_path.name}")
        
        # Process document
        extracted = doc_processor.process_document(str(file_path))
        
        if not extracted or not extracted.get('text_chunks'):
            logger.warning(f"No content extracted from {file_path.name}")
            return {
                'file': file_path.name,
                'status': 'no_content',
                'chunks': 0
            }
        
        # Extract metadata
        province = extract_province_from_path(file_path)
        doc_type = extract_document_type(file_path)
        offence_number = extracted.get('detected_offence_number')
        
        # Generate document ID
        doc_id = f"doc_{user_id}_{file_path.stem[:20]}_{hash(str(file_path)) % 100000}"
        
        # Process and embed chunks
        all_embeddings = []
        all_metadata = []
        
        for idx, chunk in enumerate(extracted['text_chunks']):
            chunk_text = chunk['content']
            if not chunk_text or len(chunk_text.strip()) < 10:
                continue
            
            # Generate embedding
            embedding = embedding_service.embed_text(chunk_text)
            
            # Create metadata
            chunk_metadata = {
                'user_id': user_id,
                'doc_id': doc_id,
                'filename': file_path.name,
                'file_path': str(file_path),
                'page': chunk.get('page', 1),
                'chunk_id': f"{doc_id}_chunk_{idx}",
                'offence_number': offence_number,
                'province': province,
                'doc_type': doc_type,
                'content': chunk_text  # Store full content for retrieval
            }
            
            all_embeddings.append(embedding[0])
            all_metadata.append(chunk_metadata)
        
        # Add to vector store
        if all_embeddings:
            import numpy as np
            embeddings_array = np.array(all_embeddings)
            vector_store.add_vectors(embeddings_array, all_metadata)
            
            logger.info(f"Added {len(all_metadata)} chunks from {file_path.name}")
        
        return {
            'file': file_path.name,
            'status': 'success',
            'chunks': len(all_metadata),
            'province': province,
            'doc_type': doc_type
        }
        
    except Exception as e:
        logger.error(f"Error processing {file_path.name}: {e}")
        return {
            'file': file_path.name,
            'status': 'error',
            'error': str(e),
            'chunks': 0
        }

def main():
    """Main ingestion function."""
    print("=" * 80)
    print("BACKEND VECTOR STORE - COMPREHENSIVE DOCUMENT INGESTION")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Find all legal documents in project directories")
    print("2. Extract text and knowledge from each document")
    print("3. Generate embeddings using Artillery embedding service")
    print("4. Store in backend's FAISS vector database")
    print("5. Make all knowledge searchable via the backend API\n")
    
    # Initialize services
    print("\n[1/4] Initializing backend services...")
    try:
        doc_processor = get_artillery_document_processor()
        embedding_service = get_artillery_embedding_service()
        
        # Initialize vector store with backend paths
        vector_store = ArtilleryVectorStore(
            dimension=384,
            description="artillery_legal_documents",
            index_path="./backend/data/artillery_legal_documents_index.bin",
            metadata_path="./backend/data/artillery_legal_documents_metadata.pkl",
            gcs_bucket=None
        )
        
        print("✅ Services initialized")
        print(f"   - Document Processor: Ready")
        print(f"   - Embedding Service: Ready (384D unified space)")
        print(f"   - Vector Store: Ready ({vector_store.ntotal:,} existing vectors)")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Find all documents
    print("\n[2/4] Scanning for documents...")
    base_path = Path(__file__).parent
    documents = find_all_documents(base_path)
    
    if not documents:
        print("❌ No documents found!")
        return 1
    
    print(f"✅ Found {len(documents)} documents to process")
    
    # Show document breakdown
    print("\nDocument breakdown:")
    by_type = {}
    for doc in documents:
        ext = doc.suffix.lower()
        by_type[ext] = by_type.get(ext, 0) + 1
    
    for ext, count in sorted(by_type.items()):
        print(f"  {ext}: {count} files")
    
    print(f"\n⚡ Auto-proceeding with ingestion of {len(documents)} documents...")
    
    # Process documents
    print(f"\n[3/4] Processing {len(documents)} documents...")
    print("This may take a while depending on document sizes...\n")
    
    results = []
    successful = 0
    failed = 0
    total_chunks = 0
    
    # Process with progress bar
    for doc_path in tqdm(documents, desc="Processing documents"):
        result = process_document(
            doc_path,
            doc_processor,
            embedding_service,
            vector_store,
            user_id="system"
        )
        results.append(result)
        
        if result['status'] == 'success':
            successful += 1
            total_chunks += result['chunks']
        else:
            failed += 1
        
        # Save periodically (every 50 documents)
        if (successful + failed) % 50 == 0:
            print(f"\n💾 Saving progress... ({vector_store.ntotal:,} vectors)")
            vector_store.save()
    
    # Save vector store
    print("\n[4/4] Saving vector store...")
    try:
        vector_store.save()
        print("✅ Vector store saved")
    except Exception as e:
        print(f"⚠️  Could not save vector store: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print(f"Total documents processed: {len(documents)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Total chunks indexed: {total_chunks:,}")
    print(f"Vector store size: {vector_store.ntotal:,} vectors")
    
    # Show statistics by province/type
    print("\nBy Document Type:")
    by_doc_type = {}
    for r in results:
        if r['status'] == 'success':
            doc_type = r.get('doc_type', 'unknown')
            by_doc_type[doc_type] = by_doc_type.get(doc_type, 0) + 1
    
    for doc_type, count in sorted(by_doc_type.items()):
        print(f"  {doc_type}: {count} documents")
    
    print("\nBy Province/State:")
    by_province = {}
    for r in results:
        if r['status'] == 'success':
            province = r.get('province', 'UNKNOWN')
            by_province[province] = by_province.get(province, 0) + 1
    
    for province, count in sorted(by_province.items()):
        print(f"  {province}: {count} documents")
    
    # Show failed files
    if failed > 0:
        print("\n⚠️  Failed files:")
        for r in results:
            if r['status'] != 'success':
                print(f"  - {r['file']}: {r.get('error', r['status'])}")
    
    print("\n" + "=" * 80)
    print("✅ INGESTION COMPLETE!")
    print("=" * 80)
    print("\nYou can now:")
    print("  1. Start the backend server: cd backend && python -m app.main")
    print("  2. Test queries: python test_toronto_speeding_scenario.py")
    print("  3. Use the frontend chat interface")
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
