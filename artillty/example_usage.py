"""
Example usage of the Unified Multi-Modal Embedding Server
Demonstrates embedding text, images, tables, and documents
"""

from unified_embedding_server import UnifiedEmbeddingServer, EmbeddingRequest
import numpy as np
from pathlib import Path


def example_text_embedding():
    """Example: Embed text content"""
    print("\n" + "="*60)
    print("📝 EXAMPLE 1: Text Embedding")
    print("="*60)
    
    server = UnifiedEmbeddingServer()
    
    # Single text
    request = EmbeddingRequest(
        content="Artificial intelligence is transforming healthcare through machine learning.",
        content_type="text"
    )
    response = server.embed(request)
    
    print(f"✅ Embedded text: {len(response.embeddings)} chunks")
    print(f"   Embedding dimension: {len(response.embeddings[0])}")
    print(f"   First 5 values: {response.embeddings[0][:5]}")
    
    # Add to index
    embeddings = np.array(response.embeddings)
    metadata = [{'chunk_id': cid, 'text': text, 'type': 'text'} 
                for cid, text in zip(response.chunk_ids, response.chunk_texts)]
    server.add_to_index(embeddings, metadata)
    
    # Search
    results = server.search("machine learning in medicine", k=1)
    print(f"\n🔍 Search results:")
    for r in results:
        print(f"   Similarity: {r['similarity']:.3f}")
        print(f"   Text: {r['metadata'].get('text', 'N/A')}")


def example_document_embedding():
    """Example: Embed a document (PDF, DOCX, etc.)"""
    print("\n" + "="*60)
    print("📄 EXAMPLE 2: Document Embedding")
    print("="*60)
    
    server = UnifiedEmbeddingServer()
    
    # Create a sample text file for demonstration
    sample_text = """
    Artificial Intelligence in Healthcare
    
    Introduction:
    Artificial intelligence is revolutionizing healthcare by enabling faster diagnosis,
    personalized treatment plans, and improved patient outcomes.
    
    Key Applications:
    1. Medical Imaging: AI can detect anomalies in X-rays, MRIs, and CT scans
    2. Drug Discovery: Machine learning accelerates pharmaceutical research
    3. Predictive Analytics: AI predicts patient risks and outcomes
    4. Virtual Assistants: Chatbots help patients with medical questions
    
    Conclusion:
    The future of healthcare is AI-powered, with technology improving lives daily.
    """
    
    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        temp_path = f.name
    
    try:
        request = EmbeddingRequest(
            file_path=temp_path,
            content_type="document"
        )
        response = server.embed(request)
        
        print(f"✅ Processed document: {temp_path}")
        print(f"   Extracted {response.num_chunks} chunks")
        print(f"   Content type: {response.content_type}")
        print(f"\n   Chunk previews:")
        for i, (cid, text) in enumerate(zip(response.chunk_ids[:3], response.chunk_texts[:3])):
            preview = text[:50] + "..." if len(text) > 50 else text
            print(f"   {i+1}. [{cid}] {preview}")
        
        # Add to index
        embeddings = np.array(response.embeddings)
        metadata = [{'chunk_id': cid, 'text': text, 'type': 'document', 'file': temp_path} 
                    for cid, text in zip(response.chunk_ids, response.chunk_texts)]
        server.add_to_index(embeddings, metadata)
        
        # Search
        results = server.search("medical imaging AI", k=2)
        print(f"\n🔍 Search results for 'medical imaging AI':")
        for r in results:
            print(f"   Similarity: {r['similarity']:.3f}")
            print(f"   Text: {r['metadata'].get('text', 'N/A')[:80]}...")
    
    finally:
        # Clean up
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)


def example_table_embedding():
    """Example: Embed a table"""
    print("\n" + "="*60)
    print("📊 EXAMPLE 3: Table Embedding")
    print("="*60)
    
    server = UnifiedEmbeddingServer()
    
    # Create sample table data
    import pandas as pd
    table_data = pd.DataFrame({
        'Product': ['Laptop', 'Phone', 'Tablet', 'Watch'],
        'Price': [999, 699, 399, 299],
        'Stock': [50, 120, 80, 200],
        'Category': ['Electronics', 'Electronics', 'Electronics', 'Wearables']
    })
    
    # Convert to CSV string
    csv_string = table_data.to_csv(index=False)
    
    request = EmbeddingRequest(
        content=csv_string,
        content_type="table"
    )
    response = server.embed(request)
    
    print(f"✅ Embedded table: {len(response.embeddings)} chunks")
    print(f"   Table has {len(table_data)} rows")
    print(f"   Columns: {', '.join(table_data.columns)}")
    
    # Add to index
    embeddings = np.array(response.embeddings)
    metadata = [{'chunk_id': cid, 'text': text, 'type': 'table'} 
                for cid, text in zip(response.chunk_ids, response.chunk_texts)]
    server.add_to_index(embeddings, metadata)
    
    # Search
    results = server.search("electronics products", k=1)
    print(f"\n🔍 Search results for 'electronics products':")
    for r in results:
        print(f"   Similarity: {r['similarity']:.3f}")
        print(f"   Content: {r['metadata'].get('text', 'N/A')}")


def example_mixed_content():
    """Example: Embed multiple types of content and search"""
    print("\n" + "="*60)
    print("🎯 EXAMPLE 4: Mixed Content Search")
    print("="*60)
    
    server = UnifiedEmbeddingServer()
    
    # Add various content types
    contents = [
        ("text", "Machine learning algorithms can predict patient outcomes."),
        ("text", "Deep learning is used for image recognition in medical scans."),
        ("text", "Natural language processing helps analyze medical records."),
        ("text", "AI chatbots assist patients with health questions 24/7."),
    ]
    
    all_embeddings = []
    all_metadata = []
    
    for content_type, content in contents:
        request = EmbeddingRequest(content=content, content_type=content_type)
        response = server.embed(request)
        
        embeddings = np.array(response.embeddings)
        metadata = [{'chunk_id': cid, 'text': text, 'type': content_type} 
                    for cid, text in zip(response.chunk_ids, response.chunk_texts)]
        
        all_embeddings.append(embeddings)
        all_metadata.extend(metadata)
    
    # Add all to index
    combined_embeddings = np.concatenate(all_embeddings, axis=0)
    server.add_to_index(combined_embeddings, all_metadata)
    
    print(f"✅ Added {len(all_metadata)} content chunks to index")
    print(f"   Total vectors in index: {server.index.ntotal}")
    
    # Search across all content
    queries = [
        "artificial intelligence in healthcare",
        "image recognition",
        "patient care technology"
    ]
    
    for query in queries:
        results = server.search(query, k=2)
        print(f"\n🔍 Query: '{query}'")
        for i, r in enumerate(results, 1):
            print(f"   {i}. Similarity: {r['similarity']:.3f}")
            print(f"      Text: {r['metadata'].get('text', 'N/A')}")


def example_save_load_index():
    """Example: Save and load index"""
    print("\n" + "="*60)
    print("💾 EXAMPLE 5: Save and Load Index")
    print("="*60)
    
    server = UnifiedEmbeddingServer()
    
    # Add some content
    request = EmbeddingRequest(
        content="This is a test document that will be saved to disk.",
        content_type="text"
    )
    response = server.embed(request)
    
    embeddings = np.array(response.embeddings)
    metadata = [{'chunk_id': cid, 'text': text} 
                for cid, text in zip(response.chunk_ids, response.chunk_texts)]
    server.add_to_index(embeddings, metadata)
    
    print(f"✅ Added {len(metadata)} vectors to index")
    
    # Save
    index_path = "test_index.index"
    server.save_index(index_path)
    print(f"✅ Saved index to {index_path}")
    
    # Create new server and load
    server2 = UnifiedEmbeddingServer()
    server2.load_index(index_path)
    print(f"✅ Loaded index: {server2.index.ntotal} vectors")
    
    # Search in loaded index
    results = server2.search("test document", k=1)
    print(f"🔍 Search in loaded index:")
    for r in results:
        print(f"   Similarity: {r['similarity']:.3f}")
        print(f"   Text: {r['metadata'].get('text', 'N/A')}")


if __name__ == "__main__":
    print("""
    🚀 Unified Multi-Modal Embedding Server - Examples
    ===================================================
    
    This script demonstrates:
    1. Text embedding
    2. Document embedding (with auto-extraction)
    3. Table embedding
    4. Mixed content search
    5. Save/load index
    
    """)
    
    try:
        example_text_embedding()
        example_document_embedding()
        example_table_embedding()
        example_mixed_content()
        example_save_load_index()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

