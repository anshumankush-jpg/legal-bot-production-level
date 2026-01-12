# Sample Data for Testing

This directory contains sample data files to test all features of the Unified Embedding Server.

## Files Included

### 1. `sample_texts.txt`
- **Type**: Text document
- **Content**: Articles about AI in healthcare
- **Use**: Test text embedding and document parsing
- **Chunks**: 10 paragraphs about healthcare AI

### 2. `products.csv`
- **Type**: Table/CSV
- **Content**: Product catalog with 15 items
- **Use**: Test table embedding
- **Columns**: Product, Category, Price, Stock, Description

### 3. `tech_articles.txt`
- **Type**: Text document
- **Content**: Articles about AI and technology
- **Use**: Test text embedding and search
- **Chunks**: 8 paragraphs about AI technology

### 4. `healthcare_data.csv`
- **Type**: Table/CSV
- **Content**: Patient medical records (anonymized)
- **Use**: Test table embedding and structured data
- **Columns**: Patient ID, Age, Diagnosis, Treatment, Outcome, Follow-up Days

### 5. `faq_document.txt`
- **Type**: Text document
- **Content**: FAQ about the embedding server
- **Use**: Test document embedding and Q&A search
- **Format**: Question-answer pairs

---

## How to Use

### Test Text Embedding
```python
from unified_embedding_server import UnifiedEmbeddingServer, EmbeddingRequest

server = UnifiedEmbeddingServer()

# Embed the text file
response = server.embed(EmbeddingRequest(
    file_path="sample_data/sample_texts.txt",
    content_type="document"
))

print(f"Embedded {response.num_chunks} chunks")
```

### Test Table Embedding
```python
# Embed the CSV file
response = server.embed(EmbeddingRequest(
    file_path="sample_data/products.csv",
    content_type="table"
))

print(f"Embedded table with {response.num_chunks} chunks")
```

### Test Search
```python
# Add documents to index
texts_response = server.embed(EmbeddingRequest(
    file_path="sample_data/sample_texts.txt",
    content_type="document"
))

import numpy as np
embeddings = np.array(texts_response.embeddings)
metadata = [{'chunk_id': cid, 'text': text, 'source': 'sample_texts.txt'} 
            for cid, text in zip(texts_response.chunk_ids, texts_response.chunk_texts)]
server.add_to_index(embeddings, metadata)

# Search
results = server.search("artificial intelligence healthcare", k=3)
for r in results:
    print(f"Similarity: {r['similarity']:.3f}")
    print(f"Text: {r['metadata']['text'][:100]}...")
```

### Test Multiple Documents
```python
# Embed multiple documents
documents = [
    "sample_data/sample_texts.txt",
    "sample_data/tech_articles.txt",
    "sample_data/faq_document.txt"
]

all_embeddings = []
all_metadata = []

for doc_path in documents:
    response = server.embed(EmbeddingRequest(
        file_path=doc_path,
        content_type="document"
    ))
    all_embeddings.append(np.array(response.embeddings))
    all_metadata.extend([{'chunk_id': cid, 'text': text, 'source': doc_path} 
                         for cid, text in zip(response.chunk_ids, response.chunk_texts)])

# Add all to index
combined = np.concatenate(all_embeddings, axis=0)
server.add_to_index(combined, all_metadata)

# Search across all documents
results = server.search("machine learning", k=5)
```

---

## Using with API Server

### Via API (curl)
```bash
# Embed a document
curl -X POST "http://localhost:8000/embed" \
  -F "file=@sample_data/sample_texts.txt" \
  -F "content_type=document"

# Search
curl -X POST "http://localhost:8000/search" \
  -F "query=artificial intelligence" \
  -F "k=5"
```

### Via Python Client
```python
from client_example import EmbeddingClient

client = EmbeddingClient()

# Embed document
result = client.embed_file("sample_data/products.csv", "table")
print(f"Embedded {result['num_chunks']} chunks")

# Add to index
client.add_to_index(
    embeddings=result['embeddings'],
    chunk_ids=result['chunk_ids'],
    chunk_texts=result['chunk_texts']
)

# Search
results = client.search("electronics products", k=3)
```

---

## Expected Results

### Text Embedding
- `sample_texts.txt`: ~10 chunks (one per paragraph)
- `tech_articles.txt`: ~8 chunks
- `faq_document.txt`: ~15 chunks (Q&A pairs)

### Table Embedding
- `products.csv`: 1-2 chunks (summary + rows)
- `healthcare_data.csv`: 1-2 chunks

### Search Examples
- Query: "artificial intelligence" → Should find chunks from `sample_texts.txt` and `tech_articles.txt`
- Query: "electronics" → Should find chunks from `products.csv`
- Query: "how does embedding work" → Should find FAQ answers

---

## Tips

1. **Start Small**: Test with one file first, then add more
2. **Check Chunks**: Print `chunk_texts` to see how documents are split
3. **Test Search**: Try different queries to see what works best
4. **Combine Types**: Mix text, tables, and documents in one index
5. **Save Index**: Save your index after adding data for faster loading later

---

**Happy Testing!** 🚀

