"""
Example client for the Unified Embedding Server API
Demonstrates how to use the REST API from Python
"""

import requests
import json
from pathlib import Path


class EmbeddingClient:
    """Client for the Unified Embedding Server API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def embed_text(self, text: str, content_type: str = "text"):
        """Embed text content"""
        response = requests.post(
            f"{self.base_url}/embed",
            data={
                "content": text,
                "content_type": content_type
            }
        )
        response.raise_for_status()
        return response.json()
    
    def embed_file(self, file_path: str, content_type: str = "auto"):
        """Embed a file (document, image, table, etc.)"""
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            data = {'content_type': content_type}
            response = requests.post(
                f"{self.base_url}/embed",
                files=files,
                data=data
            )
        response.raise_for_status()
        return response.json()
    
    def embed_batch(self, texts: list, content_type: str = "text"):
        """Embed multiple texts at once"""
        response = requests.post(
            f"{self.base_url}/embed/batch",
            data={
                "contents": json.dumps(texts),
                "content_type": content_type
            }
        )
        response.raise_for_status()
        return response.json()
    
    def add_to_index(self, embeddings: list, chunk_ids: list, chunk_texts: list, metadata: list = None):
        """Add embeddings to the FAISS index"""
        payload = {
            "embeddings": json.dumps(embeddings),
            "chunk_ids": json.dumps(chunk_ids),
            "chunk_texts": json.dumps(chunk_texts)
        }
        if metadata:
            payload["metadata"] = json.dumps(metadata)
        
        response = requests.post(
            f"{self.base_url}/index/add",
            json={
                "embeddings": embeddings,
                "chunk_ids": chunk_ids,
                "chunk_texts": chunk_texts,
                "metadata": metadata or []
            }
        )
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str, k: int = 5):
        """Search for similar content"""
        response = requests.post(
            f"{self.base_url}/search",
            data={
                "query": query,
                "k": str(k)
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self):
        """Get index statistics"""
        response = requests.get(f"{self.base_url}/index/stats")
        response.raise_for_status()
        return response.json()
    
    def save_index(self, path: str):
        """Save index to disk"""
        response = requests.post(
            f"{self.base_url}/index/save",
            data={"path": path}
        )
        response.raise_for_status()
        return response.json()
    
    def load_index(self, path: str):
        """Load index from disk"""
        response = requests.post(
            f"{self.base_url}/index/load",
            data={"path": path}
        )
        response.raise_for_status()
        return response.json()


def example_usage():
    """Example usage of the client"""
    print("[*] Embedding Server Client Example\n")
    
    # Initialize client
    client = EmbeddingClient()
    
    # 1. Embed text
    print("[1] Embedding text...")
    result = client.embed_text("Machine learning is transforming healthcare.")
    print(f"   [OK] Embedded: {result['num_chunks']} chunks")
    print(f"   Embedding dimension: {len(result['embeddings'][0])}")
    
    # 2. Add to index
    print("\n[2] Adding to index...")
    add_result = client.add_to_index(
        embeddings=result['embeddings'],
        chunk_ids=result['chunk_ids'],
        chunk_texts=result['chunk_texts'],
        metadata=[{'source': 'example'}]
    )
    print(f"   [OK] Added {add_result['added']} vectors")
    
    # 3. Search
    print("\n[3] Searching...")
    search_result = client.search("artificial intelligence in medicine", k=1)
    print(f"   [OK] Found {search_result['count']} results")
    if search_result['results']:
        r = search_result['results'][0]
        print(f"   Top result: similarity={r['similarity']:.3f}")
        print(f"   Text: {r['metadata'].get('text', 'N/A')[:60]}...")
    
    # 4. Get stats
    print("\n[4] Index statistics...")
    stats = client.get_stats()
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Embedding dimension: {stats['embedding_dim']}")
    
    # 5. Batch embedding
    print("\n[5] Batch embedding...")
    texts = [
        "Deep learning for image recognition",
        "Natural language processing",
        "Computer vision applications"
    ]
    batch_result = client.embed_batch(texts)
    print(f"   [OK] Embedded {batch_result['num_chunks']} texts")
    
    print("\n[SUCCESS] All examples completed!")


if __name__ == "__main__":
    try:
        example_usage()
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server.")
        print("   Make sure the server is running: python api_server.py")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

