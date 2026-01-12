#!/usr/bin/env python3
"""
Bulk Document Ingestion Script for PLAZA-AI
Reads all documents from various directories and stores them in FAISS vector store
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Artillery components
from artillty.multi_modal_embedding_service import get_embedding_service
from artillty.document_processor import get_document_processor
from artillty.faiss_vector_store import get_vector_store, FAISSVectorStore

# Import legal category mapper
try:
    from legal_category_mapper import (
        classify_legal_category,
        detect_jurisdiction,
        get_category_display_name,
        get_category_priority
    )
    USE_CATEGORY_MAPPER = True
except ImportError:
    logger.warning("legal_category_mapper not found, using basic classification")
    USE_CATEGORY_MAPPER = False

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
    "data",
    "docs/downloaded_pdfs",
    "us_state_codes",
    "us_traffic_laws",
    "usa",
    "usa_case_law",
    "usa_criminal_law",
    "enhanced_legal_text"  # Add enhanced legal datasets
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
        'illinois': 'IL', 'pennsylvania': 'PA', 'ohio': 'OH', 'georgia': 'GA'
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
    # Use enhanced category mapper if available
    if USE_CATEGORY_MAPPER:
        try:
            jurisdiction = detect_jurisdiction(file_path)
            primary_category, subcategory, tags = classify_legal_category(file_path, jurisdiction)
            return primary_category
        except Exception as e:
            logger.warning(f"Category mapper failed for {file_path.name}: {e}, using basic classification")
    
    # Fallback to basic classification
    path_str = str(file_path).lower()
    
    if 'traffic' in path_str or 'highway' in path_str or 'motor_vehicle' in path_str:
        return 'regulatory_traffic'
    elif 'criminal' in path_str:
        return 'criminal'
    elif 'case_law' in path_str:
        return 'case_law'
    elif 'demerit' in path_str:
        return 'regulatory_traffic'  # Demerit tables are traffic-related
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
        
        # Enhanced category information
        jurisdiction = None
        subcategory = None
        category_tags = []
        category_display = None
        category_priority = None
        
        if USE_CATEGORY_MAPPER:
            try:
                jurisdiction = detect_jurisdiction(file_path)
                primary_category, subcategory, category_tags = classify_legal_category(file_path, jurisdiction)
                category_display = get_category_display_name(primary_category)
                category_priority = get_category_priority(primary_category)
                # Update doc_type with primary category if different
                if primary_category != doc_type:
                    doc_type = primary_category
            except Exception as e:
                logger.debug(f"Enhanced categorization failed: {e}")
        
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
                'content': chunk_text[:500]  # Store first 500 chars for reference
            }
            
            # Add enhanced category metadata if available
            if USE_CATEGORY_MAPPER and jurisdiction:
                chunk_metadata.update({
                    'jurisdiction': jurisdiction,
                    'legal_category': doc_type,
                    'category_display': category_display,
                    'subcategory': subcategory,
                    'category_tags': category_tags,
                    'category_priority': category_priority,
                    'is_high_priority': category_priority is not None and category_priority < 4
                })
            
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
    print("PLAZA-AI Bulk Document Ingestion")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Find all documents in project directories")
    print("2. Extract text and knowledge from each document")
    print("3. Generate embeddings using SentenceTransformers/CLIP")
    print("4. Store in FAISS vector database")
    print("5. Make all knowledge searchable via RAG\n")
    
    # Initialize services
    print("\n[1/4] Initializing services...")
    try:
        doc_processor = get_document_processor()
        embedding_service = get_embedding_service()
        # Initialize vector store with proper parameters
        vector_store = get_vector_store(
            dimension=384,
            description="artillery_legal_documents",
            gcs_bucket=None
        )
        print("SUCCESS: Services initialized")
        print(f"   - Document Processor: Ready")
        print(f"   - Embedding Service: Ready (384D unified space)")
        print(f"   - Vector Store: Ready ({vector_store.index.ntotal} existing vectors)")
    except Exception as e:
        print(f"ERROR: Failed to initialize services: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Find all documents
    print("\n[2/4] Scanning for documents...")
    base_path = Path(__file__).parent
    documents = find_all_documents(base_path)
    
    if not documents:
        print("ERROR: No documents found!")
        return 1
    
    print(f"SUCCESS: Found {len(documents)} documents to process")
    
    # Show document breakdown
    print("\nDocument breakdown:")
    by_type = {}
    for doc in documents:
        ext = doc.suffix.lower()
        by_type[ext] = by_type.get(ext, 0) + 1
    
    for ext, count in sorted(by_type.items()):
        print(f"  {ext}: {count} files")
    
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
    
    # Save vector store
    print("\n[4/4] Saving vector store...")
    try:
        vector_store.save()
        print("SUCCESS: Vector store saved")
    except Exception as e:
        print(f"WARNING: Could not save vector store: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print(f"Total documents processed: {len(documents)}")
    print(f"SUCCESS: Successful: {successful}")
    print(f"FAILED: Failed: {failed}")
    print(f"Total chunks indexed: {total_chunks}")
    print(f"Vector store size: {vector_store.index.ntotal} vectors")
    
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
        print("\nWARNING: Failed files:")
        for r in results:
            if r['status'] != 'success':
                print(f"  - {r['file']}: {r.get('error', r['status'])}")
    
    print("\n" + "=" * 80)
    print("SUCCESS: INGESTION COMPLETE!")
    print("=" * 80)
    print("\nYou can now ask questions about the documents using the chat interface.")
    print("All knowledge has been stored in the FAISS vector database.")
    print("\nTo query the knowledge, use:")
    print("  - Frontend chat interface at http://localhost:4200")
    print("  - API endpoint: POST /api/artillery/chat")
    print("  - API endpoint: POST /api/artillery/search")
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nWARNING: Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
