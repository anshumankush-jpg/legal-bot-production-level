"""
Fix Pinecone index - Delete old 384-dim index and create new 1536-dim index.
This fixes the dimension mismatch that causes 6+ minute query times.
"""
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("FIXING PINECONE INDEX - DIMENSION MISMATCH")
print("=" * 80)
print()
print("Problem: Your Pinecone index has 384 dimensions (sentence-transformers)")
print("         But you're using OpenAI embeddings which produce 1536 dimensions")
print()
print("Solution: Delete old index -> Create new 1536-dim index -> Re-ingest documents")
print("=" * 80)
print()

# Get Pinecone credentials
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-docs")

if not PINECONE_API_KEY:
    print("[ERROR] PINECONE_API_KEY not found in .env file")
    sys.exit(1)

print("[1/4] Connecting to Pinecone...")
try:
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print("[OK] Connected to Pinecone")
except Exception as e:
    print(f"[ERROR] Failed to connect: {e}")
    sys.exit(1)

print(f"\n[2/4] Checking existing index '{PINECONE_INDEX_NAME}'...")
try:
    existing_indexes = pc.list_indexes()
    index_names = [idx.name for idx in existing_indexes]
    
    if PINECONE_INDEX_NAME in index_names:
        print(f"[OK] Found existing index: {PINECONE_INDEX_NAME}")
        
        # Get index stats
        index = pc.Index(PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        current_dimension = stats.get('dimension', 'unknown')
        total_vectors = stats.get('total_vector_count', 0)
        
        print(f"   Current dimension: {current_dimension}")
        print(f"   Current vectors: {total_vectors}")
        
        if current_dimension == 384:
            print(f"\n[WARNING] CONFIRMED: Index has WRONG dimension (384 instead of 1536)")
            print(f"   Deleting old index...")
            pc.delete_index(PINECONE_INDEX_NAME)
            print(f"[OK] Deleted old index")
            
            # Wait for deletion to complete
            print("   Waiting 10 seconds for deletion to complete...")
            time.sleep(10)
        elif current_dimension == 1536:
            print(f"\n[OK] Index already has correct dimension (1536)!")
            print(f"   No need to recreate. Your backend should work now.")
            sys.exit(0)
    else:
        print(f"[INFO] Index '{PINECONE_INDEX_NAME}' doesn't exist yet")
        
except Exception as e:
    print(f"[ERROR] Error checking index: {e}")
    sys.exit(1)

print(f"\n[3/4] Creating new index with 1536 dimensions (OpenAI)...")
try:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,  # OpenAI text-embedding-ada-002 dimension
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print(f"[OK] Created new index: {PINECONE_INDEX_NAME}")
    print(f"   Dimension: 1536")
    print(f"   Metric: cosine")
    print(f"   Cloud: AWS us-east-1")
    
    # Wait for index to be ready
    print("\n   Waiting for index to initialize...")
    time.sleep(20)
    
except Exception as e:
    print(f"[ERROR] Failed to create index: {e}")
    sys.exit(1)

print(f"\n[4/4] Verifying new index...")
try:
    index = pc.Index(PINECONE_INDEX_NAME)
    stats = index.describe_index_stats()
    
    print(f"[OK] Index is ready!")
    print(f"   Dimension: {stats.get('dimension')}")
    print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
    
except Exception as e:
    print(f"[ERROR] Error verifying index: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("[SUCCESS] Pinecone index fixed with correct dimensions (1536)")
print("=" * 80)
print()
print("Next Steps:")
print("   1. Re-run ingestion: python ingest_to_pinecone.py")
print("   2. This will upload all 1050 documents with OpenAI embeddings")
print("   3. Takes ~10-15 minutes and costs ~$1-2")
print("   4. Then your backend will work FAST! (queries in 5-10 seconds)")
print()
print("=" * 80)
