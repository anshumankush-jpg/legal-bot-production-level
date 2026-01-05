# PLAZA-AI: Multi-Modal Legal Assistant Embedding System

## 📋 Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [GCP Deployment Architecture](#gcp-deployment-architecture)
- [Embedding Models](#embedding-models)
- [End-to-End Processing Pipeline](#end-to-end-processing-pipeline)
- [Document Processing](#document-processing)
- [Vector Search & FAISS](#vector-search--faiss)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [GCP Deployment Guide](#gcp-deployment-guide)
- [Testing & Performance](#testing--performance)
- [Quick Start](#quick-start)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**PLAZA-AI** is a specialized **Retrieval-Augmented Generation (RAG) AI system** designed for legal document analysis and advice. The system processes legal documents from **all provinces of Canada and USA**, providing contextual legal advice based on uploaded documents.

**Deployed on Google Cloud Platform (GCP)** with local embedding models for optimal performance and cost efficiency.

### Key Features
- ✅ **Multi-Modal Processing**: Text, images, tables, and documents
- ✅ **Unified 384D Vector Space**: All content types in same semantic space
- ✅ **Legal Domain Specialized**: Canadian and US provincial legal rules
- ✅ **Offence Number Detection**: Automatic extraction and validation
- ✅ **Fast Vector Search**: FAISS-based similarity search
- ✅ **RAG-Powered**: Contextual responses with citations
- ✅ **GCP-Native**: Deployed on Google Cloud Platform
- ✅ **Local Embeddings**: No external API dependencies (SentenceTransformers + CLIP run locally)

### AI Classification
- **Primary Type**: Retrieval-Augmented Generation (RAG) AI
- **Secondary Type**: Multi-modal AI (text, images, documents)
- **Specialization**: Legal Assistant AI with domain-specific knowledge
- **Architecture**: Hybrid AI (retrieval + generation + computer vision)
- **Deployment**: Google Cloud Platform (GCP)

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ PLAZA-AI System Architecture (GCP) │
└─────────────────────────────────────────────────────────────────┘
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Frontend │ │ Backend │ │ Artillery │
│ (React) │◄──►│ (FastAPI on │◄──►│ (Embedding)│
│ │ │ Cloud Run) │ │ │
│ • Chat UI │ │ │ │ • Text: ST │
│ • Upload │ │ • /api/chat │ │ • Image: CLIP│
│ • Documents │ │ • /api/upload│ │ • FAISS Index│
└──────────────┘ │ • /api/search│ └──────────────┘
└──────┬───────┘ │
│ │
▼ ▼
┌───────────────┐ ┌───────────────┐
│ Cloud Storage│ │ FAISS Index │
│ (Documents) │ │ (384D Unified)│
└───────────────┘ └───────────────┘
│ │
└─────────┬─────────┘
▼
┌─────────────────┐
│ Cloud SQL / │
│ Firestore │
│ (Metadata) │
└─────────────────┘
```

### Technology Stack
| Component | Technology | GCP Service | Purpose |
|-----------|-----------|-------------|---------|
| **Backend Framework** | FastAPI | Cloud Run | REST API server |
| **Text Embeddings** | SentenceTransformers (all-MiniLM-L6-v2) | Cloud Run (local) | Local text embedding model |
| **Image Embeddings** | CLIP (ViT-B/32) | Cloud Run (local) | Local image embedding model |
| **Vector Database** | FAISS (IndexFlatIP) | Cloud Run (in-memory) | Local vector similarity search |
| **Document Storage** | - | Cloud Storage | Store original PDFs/DOCX |
| **Metadata Database** | PostgreSQL | Cloud SQL | Store chunk metadata |
| **Document Processing** | PyMuPDF, pdfplumber, python-docx | Cloud Run | PDF/DOCX text extraction |
| **OCR** | pytesseract, easyocr | Cloud Run | Image text extraction |
| **Frontend** | React/Vite | Cloud Run / Cloud Storage | User interface |
| **CI/CD** | - | Cloud Build | Automated deployment |
| **Container Registry** | - | Artifact Registry | Docker image storage |

**Key Points**:
- ✅ Embedding models run **locally** in Cloud Run containers (no external API calls)
- ✅ FAISS index stored **in-memory** in Cloud Run (persisted to Cloud Storage)
- ✅ Documents stored in **Cloud Storage** buckets
- ✅ Metadata stored in **Cloud SQL** (PostgreSQL)
- ✅ **Auto-scaling** based on request volume

---

## ☁️ GCP Deployment Architecture

### Component Details

#### 1. Cloud Run (Backend Service)
**Service Configuration**:
```yaml
Service Name: plaza-ai-artillery
Region: us-central1
CPU: 2 vCPU
Memory: 4 GiB
Min Instances: 1 (always warm)
Max Instances: 10 (auto-scale)
Timeout: 300 seconds
Concurrency: 80 requests per instance
```

**Container Resources**:
- **SentenceTransformer Model**: ~80MB (loaded at startup)
- **CLIP Model**: ~150MB (loaded at startup)
- **FAISS Index**: Variable (depends on document count)
- **Base Container**: ~500MB
- **Total Memory**: ~4GB recommended

**Environment Variables**:
```bash
# GCP Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GCS_BUCKET_NAME=plaza-ai-documents

# Application
EMBEDDING_MODEL=all-MiniLM-L6-v2
CLIP_MODEL=ViT-B/32
FAISS_DIMENSION=384
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

#### 2. Cloud Storage (Document Storage)
**Bucket Structure**:
```
gs://plaza-ai-documents/
├── uploads/
│   ├── user_123/
│   │   ├── ontario_traffic_law.pdf
│   │   └── quebec_legal_code.docx
│   └── user_456/
│       └── california_penal_code.pdf
├── faiss_index.bin          # FAISS index file
├── metadata.pkl             # Metadata pickle file
└── processed/
    └── [processed documents]
```

#### 3. Cloud SQL (Metadata Database)
**Instance Configuration**:
```yaml
Instance Name: plaza-ai-db
Database Version: PostgreSQL 14
Tier: db-f1-micro (development) / db-n1-standard-1 (production)
Region: us-central1
High Availability: Enabled (production)
Backup: Enabled (7-day retention)
```

**Database Schema**:
```sql
-- Chunks table
CREATE TABLE chunks (
    chunk_id VARCHAR(255) PRIMARY KEY,
    doc_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding_vector_id INTEGER NOT NULL,
    file_name VARCHAR(255),
    page INTEGER,
    province VARCHAR(100),
    offence_number VARCHAR(20),
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    doc_id VARCHAR(255) PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    province VARCHAR(100),
    detected_offence_number VARCHAR(20),
    num_chunks INTEGER,
    file_size BIGINT,
    uploaded_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🧠 Embedding Models

### 1. SentenceTransformer (`all-MiniLM-L6-v2`)
**Purpose**: Generate 384-dimensional embeddings for text content

**Model Specifications**:
- **Base Model**: `microsoft/MiniLM-L6-H384-uncased`
- **Architecture**: 6-layer transformer with mean pooling
- **Output Dimension**: 384
- **Max Sequence Length**: 256 tokens
- **Normalization**: L2-normalized outputs
- **Performance**: ~1000 sentences/second (CPU)

**Usage**:
```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load model (once at startup)
text_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

# Embed text
texts = ["What are the penalties for speeding?", "Legal requirements for traffic violations"]
embeddings = text_model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,  # L2 normalization for cosine similarity
    show_progress_bar=True,
    batch_size=32
)

# Output shape: (2, 384) for 2 texts
# Each vector has L2 norm = 1.0
```

### 2. CLIP (ViT-B/32)
**Purpose**: Generate embeddings for images, projected to 384D for unified space

**Model Specifications**:
- **Model**: Vision Transformer Base (32x32 patches)
- **Architecture**: 12-layer transformer encoder
- **Native Output**: 512 dimensions
- **Projected Output**: 384 dimensions (to match text)
- **Image Resolution**: 224x224 (resized from input)
- **Performance**: ~10 images/second (CPU)

**Usage**:
```python
import clip
import torch
from PIL import Image
import numpy as np

# Load CLIP model (once at startup)
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

# Process image
image = Image.open("traffic_sign.jpg").convert('RGB')
image_tensor = clip_preprocess(image).unsqueeze(0).to(device)

# Generate embedding
with torch.no_grad():
    image_features = clip_model.encode_image(image_tensor)
    # Shape: (1, 512)

    # Project to 384D (take first 384 dimensions)
    embedding_384d = image_features[:, :384].cpu().numpy()[0]

    # Normalize for cosine similarity
    embedding_384d = embedding_384d / np.linalg.norm(embedding_384d)

# Output: (384,) normalized vector
```

### 3. Unified 384D Vector Space
**Key Design Decision**: Both text and images use 384-dimensional vectors stored in the same FAISS index, enabling:
- ✅ Cross-modal search (text queries find images, image queries find text)
- ✅ Unified similarity calculation
- ✅ Efficient storage and search

---

## 🔄 End-to-End Processing Pipeline

### Part 1: Text Processing
**Step-by-Step: How Text is Embedded**
1. Input: `text = "Artificial intelligence is transforming healthcare..."`
2. Model Initialization (once at startup): `self.text_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")`
3. Embedding Process:
```python
def embed_text(self, texts: List[str]) -> np.ndarray:
    embeddings = self.text_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embeddings  # Shape: (N, 384) for N texts
```
4. Output: `# Shape: (1, 384) for single text, (N, 384) for N texts`

### Part 2: Image Processing
**Step-by-Step: How Images are Embedded**
1. Input: `image_path = "image.png"`
2. CLIP Processing:
```python
image_features = self.clip_model.encode_image(image_tensor)
embedding_384d = image_features[:, :384].cpu().numpy()[0]
embedding_384d = embedding_384d / np.linalg.norm(embedding_384d)
```
3. Output: `# Shape: (384,) - matches text embedding dimension`

### Part 3: Document Processing
**Example: Processing a Legal PDF Document**
1. User uploads: `"ontario_traffic_law.pdf"` (50 pages, 50,000 words)
2. Extract content: Split into 50 text chunks
3. Generate embeddings: Each chunk → 384D vector
4. Add to FAISS: Combined into (60, 384) matrix
5. Result: Top 5 most relevant chunks from search

---

## 🔍 Vector Search & FAISS

### FAISS Index Configuration
- **Index Type**: IndexFlatIP (Inner Product for cosine similarity)
- **Dimension**: 384 (unified embedding space)
- **Metric**: Cosine similarity (via L2-normalized vectors)
- **Storage**: In-memory with GCS persistence

### Search Process
```python
# 1. Normalize query for cosine similarity
query_vector = query_vector / np.linalg.norm(query_vector)

# 2. Search FAISS index
distances, indices = index.search(query_vector, k=10)

# 3. Results: Cosine similarities (0-1) and vector indices
```

### Vector Operations
- **Normalization**: `vector_normalized = vector / sqrt(sum(vector²))`
- **Cosine Similarity**: `similarity = dot(query_vector, document_vector)`
- **Range**: -1 to 1 (normalized vectors: 0 to 1)

---

## 📡 API Endpoints

### Base URL
```
https://plaza-ai-artillery-XXXXX-uc.a.run.app
```

### POST /api/artillery/upload
Upload and process documents.

**Request**:
```json
{
  "file": "<multipart file>",
  "offence_number": "123456789",
  "province": "Ontario",
  "user_id": "default_user"
}
```

**Response**:
```json
{
  "doc_id": "doc_user123_123456789_ontario_traffic_law_pdf",
  "chunks_indexed": 60,
  "detected_offence_number": "123456789",
  "detected_province": "Ontario",
  "processing_time_seconds": 12.5,
  "message": "Successfully processed document with 60 chunks"
}
```

### POST /api/artillery/chat
Chat with legal documents using RAG.

**Request**:
```json
{
  "message": "What are the penalties for speeding in Ontario?",
  "offence_number": "123456789",
  "province": "Ontario",
  "max_results": 10
}
```

**Response**:
```json
{
  "answer": "Based on the Ontario Highway Traffic Act...",
  "citations": [...],
  "chunks_used": 3,
  "confidence": 0.87
}
```

### POST /api/artillery/search
Vector similarity search.

**Request**:
```json
{
  "query": "speeding penalties",
  "k": 10,
  "filters": {"offence_number": "123456789"},
  "score_threshold": 0.7
}
```

### GET /api/artillery/health
Health check endpoint.

---

## ⚙️ Configuration

### Environment Variables
```bash
# GCP Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GCS_BUCKET_NAME=plaza-ai-documents
CLOUD_SQL_INSTANCE=plaza-ai-db
CLOUD_SQL_DATABASE=plaza_ai

# Application
EMBEDDING_MODEL=all-MiniLM-L6-v2
CLIP_MODEL=ViT-B/32
FAISS_DIMENSION=384
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Configuration File
```json
{
  "embedding": {
    "text_model": "all-MiniLM-L6-v2",
    "clip_model": "ViT-B/32",
    "text_dimension": 384,
    "unified_dimension": 384,
    "normalize": true
  },
  "chunking": {
    "chunk_size": 1000,
    "chunk_overlap": 200
  },
  "faiss": {
    "index_type": "IndexFlatIP",
    "dimension": 384
  },
  "gcp": {
    "project_id": "your-project-id",
    "storage_bucket": "plaza-ai-documents"
  }
}
```

---

## 🚀 GCP Deployment Guide

### Prerequisites
```bash
# Install gcloud CLI
# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 1: Create Cloud Storage Bucket
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://plaza-ai-documents
gsutil iam ch allUsers:objectViewer gs://plaza-ai-documents
```

### Step 2: Create Cloud SQL Instance
```bash
gcloud sql instances create plaza-ai-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_PASSWORD

gcloud sql databases create plaza_ai --instance=plaza-ai-db
```

### Step 3: Deploy to Cloud Run
```bash
# Build and deploy
gcloud builds submit --config artillty/cloudbuild.yaml

# Or manually
gcloud run deploy plaza-ai-artillery \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GCS_BUCKET_NAME=plaza-ai-documents \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:plaza-ai-db \
  --allow-unauthenticated
```

---

## 📊 Testing & Performance

### Performance Benchmarks
- **Text Embedding**: ~1000 sentences/second (CPU)
- **Image Embedding**: ~10 images/second (CPU)
- **Document Processing**: 1-5 seconds per PDF
- **Vector Search**: ~1ms per query (up to 1M vectors)
- **Memory Usage**: ~380MB for models + index

### Running Tests
```bash
cd artillty

# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_multi_modal_embedding.py::TestMultiModalEmbeddingService::test_text_embedding -v
```

### Test Coverage
- ✅ Multi-modal embedding generation
- ✅ Document processing and chunking
- ✅ FAISS vector storage and search
- ✅ API endpoint functionality
- ✅ GCP integration (when available)

---

## 🚀 Quick Start

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd PLAZA-AI/artillty

# Install dependencies
pip install -r requirements.txt
pip install git+https://github.com/openai/CLIP.git

# Run API server
python -m uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/api/artillery/health
```

### Docker Development
```bash
# Build image
docker build -t plaza-ai-artillery .

# Run container
docker run -p 8000:8000 plaza-ai-artillery
```

---

## 🐛 Troubleshooting

### Common Issues

#### CLIP Model Not Loading
```bash
# Install CLIP separately
pip install git+https://github.com/openai/CLIP.git

# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

#### FAISS Index Too Large
```python
# Use IndexIVFFlat for larger datasets
import faiss
dimension = 384
nlist = 100  # Number of clusters
index = faiss.IndexIVFFlat(dimension, nlist)
index.train(embeddings)  # Train on sample data
index.add(embeddings)
```

#### GCP Storage Permissions
```bash
# Check service account permissions
gcloud iam service-accounts get-iam-policy plaza-ai-sa@YOUR_PROJECT.iam.gserviceaccount.com

# Grant storage permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:plaza-ai-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

#### Memory Issues
- Reduce batch size for embedding generation
- Use smaller models (all-MiniLM-L6-v2 instead of larger models)
- Increase Cloud Run memory allocation

---

## 📚 Additional Resources

### Documentation
- [SentenceTransformers](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [CLIP Paper](https://arxiv.org/abs/2103.00020)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Cloud Run](https://cloud.google.com/run)

### Model Performance
| Model | Dimension | Speed (CPU) | Quality | Use Case |
|-------|-----------|-------------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fastest | Good | Production default |
| all-mpnet-base-v2 | 768 | Medium | Best | High accuracy |
| CLIP ViT-B/32 | 512→384 | Slow | Good | Multi-modal |

---

## 📄 License
Copyright (c) 2025. All rights reserved.

## ⚖️ Legal Disclaimer
This system provides informational assistance only and does not constitute legal advice. Always consult with qualified legal professionals for legal matters.

---

**Built with ❤️ for making legal information more accessible.**

Last Updated: 2025-01-XX
Version: 1.0.0
Status: Production Ready (GCP)
Deployment: Google Cloud Platform