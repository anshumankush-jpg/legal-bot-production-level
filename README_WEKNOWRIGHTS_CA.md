# 🤖 weknowrights.CA - GenAI RAG Chatbot Build Guide

> Complete guide to building an enterprise-grade Retrieval-Augmented Generation (RAG) chatbot on Google Cloud Platform (GCP) based on the existing Azure-based architecture.

---

## 📋 Table of Contents

1. [System Overview](#-system-overview)
2. [Architecture](#-architecture)
3. [Technology Stack](#-technology-stack)
4. [Core Features & Rules](#-core-features--rules)
5. [Embedding Models & AI Configuration](#-embedding-models--ai-configuration)
6. [Project Structure](#-project-structure)
7. [GCP Services Setup](#-gcp-services-setup)
8. [Backend Implementation](#-backend-implementation)
9. [Frontend Implementation](#-frontend-implementation)
10. [Configuration](#-configuration)
11. [Deployment](#-deployment)
12. [Security](#-security)

---

## 🎯 System Overview

**weknowrights.CA** is a production-ready RAG (Retrieval-Augmented Generation) chatbot that:

- Answers questions based on your organization's documents
- Uses **Vertex AI Search** (or **Vertex AI Vector Search**) for semantic document retrieval
- Leverages **Vertex AI (Gemini/GPT-4)** for intelligent responses
- Stores chat history in **Cloud Firestore** or **Cloud SQL**
- Provides real-time streaming responses
- Includes analytics and feedback tracking

### How RAG Works

```
User Question → Embedding → Vector Search → Context Retrieval → LLM + Context → Response
```

1. **User asks a question**
2. **Embed the question** using Vertex AI embeddings (text-embedding-004 or text-embedding-ada-002)
3. **Search documents** in Vertex AI Vector Search using vector similarity
4. **Retrieve relevant chunks** (parent-child retrieval pattern)
5. **Send context + question to LLM** (Gemini Pro or GPT-4)
6. **Stream response** back to user with citations

---

## 🏗 Architecture

### High-Level Architecture (GCP)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           GOOGLE CLOUD PLATFORM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────┐ │
│  │   Browser   │───▶│   Angular   │───▶│     FastAPI Backend         │ │
│  │   (User)    │    │  Frontend   │    │   (Cloud Run/App Engine)    │ │
│  └─────────────┘    └─────────────┘    │                             │ │
│                                         │  ┌─────────────────────┐   │ │
│                                         │  │ Cognitive Service   │   │ │
│                                         │  │ (RAG Pipeline)      │   │ │
│                                         │  └──────────┬──────────┘   │ │
│                                         └─────────────┼──────────────┘ │
│                                                       │                 │
│         ┌─────────────────────────────────────────────┼─────────────┐  │
│         │                                             │             │  │
│         ▼                                             ▼             ▼  │
│  ┌─────────────┐    ┌─────────────────────┐   ┌─────────────────┐    │
│  │  Firestore  │    │ Vertex AI Vector    │   │   Vertex AI     │    │
│  │  / Cloud SQL│    │ Search / Matching   │   │ (Gemini/GPT-4)  │    │
│  │             │    │ Engine              │   │                 │    │
│  │ • Chats     │    │ • Parent Chunks     │   │ • Chat Model    │    │
│  │ • Users     │    │ • Child Chunks     │   │ • Embedding     │    │
│  │ • Feedback  │    │ • Embeddings        │   │ • Summarization │    │
│  └─────────────┘    └─────────────────────┘   └─────────────────┘    │
│                                                                        │
│  ┌─────────────┐    ┌─────────────────────┐   ┌─────────────────┐    │
│  │ Cloud       │    │ Secret Manager      │   │ Cloud Logging   │    │
│  │ Storage     │    │ (Secrets)           │   │ (Monitoring)     │    │
│  └─────────────┘    └─────────────────────┘   └─────────────────┘    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Parent-Child Chunk Retrieval Pattern

```
┌──────────────────────────────────────────────────────────────────┐
│                    DOCUMENT CHUNKING STRATEGY                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Original Document                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Page 1: Introduction to Rights and Legal Systems...     │   │
│  │  Page 2: Legal Procedures...                             │   │
│  │  Page 3: Rights Documentation...                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PARENT CHUNKS (Large context - 2000 tokens)             │   │
│  │  ┌────────────────┐  ┌────────────────┐                  │   │
│  │  │ Parent ID: P1  │  │ Parent ID: P2  │                  │   │
│  │  │ Full Section   │  │ Full Section   │                  │   │
│  │  └────────┬───────┘  └────────┬───────┘                  │   │
│  │           │                   │                          │   │
│  │           ▼                   ▼                          │   │
│  │  CHILD CHUNKS (Small - 500 tokens, used for search)      │   │
│  │  ┌────────┐ ┌────────┐  ┌────────┐ ┌────────┐           │   │
│  │  │Child 1 │ │Child 2 │  │Child 3 │ │Child 4 │           │   │
│  │  │(P1)    │ │(P1)    │  │(P2)    │ │(P2)    │           │   │
│  │  └────────┘ └────────┘  └────────┘ └────────┘           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Search Process:                                                  │
│  1. Vector search on CHILD chunks (more precise)                 │
│  2. Retrieve associated PARENT chunks (more context)             │
│  3. Send PARENT context to LLM for comprehensive answers           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Technology Stack

### Backend Libraries (requirements.txt)

```txt
# Web Framework
fastapi              # Modern async web framework
uvicorn[standard]    # ASGI server with hot reload

# Data Validation
pydantic             # Data validation using Python type hints
pydantic[email]      # Email validation support
pydantic-settings    # Settings management from env vars

# HTTP Client
httpx                # Async HTTP client

# Environment & Config
python-dotenv        # Load .env files

# Authentication
PyJWT[crypto]        # JWT token handling

# Google Cloud Services
google-cloud-firestore      # Firestore client
google-cloud-storage        # Cloud Storage client
google-cloud-secret-manager # Secret Manager integration
google-cloud-logging        # Cloud Logging
google-cloud-aiplatform     # Vertex AI client
google-auth                 # Google authentication

# AI/ML
langchain            # LLM orchestration framework
langchain-google-vertexai   # Vertex AI integration
langchain-openai     # OpenAI integration (if using OpenAI)
openai               # OpenAI API client (if using OpenAI)

# Document Processing
PyPDF2               # PDF handling
tiktoken             # Token counting
```

### Frontend Stack

```json
{
  "dependencies": {
    "@angular/core": "^19.0.1",
    "@angular/material": "^19.2.8",
    "@angular/router": "^19.0.1",
    "rxjs": "~7.8.0",
    "chart.js": "^4.4.8",
    "primeng": "^19.0.10"
  }
}
```

### GCP Services Required

| Service | Purpose | Alternative |
|---------|---------|-------------|
| **Vertex AI** | Gemini Pro/GPT-4 for chat, text-embedding-004 for vectors | OpenAI API |
| **Vertex AI Vector Search** | Vector + hybrid search index | Matching Engine / Pinecone |
| **Cloud Firestore** | NoSQL database for chat history | Cloud SQL (PostgreSQL) |
| **Cloud Storage** | Document storage | - |
| **Secret Manager** | Secrets management | - |
| **Cloud Run** | Backend hosting | App Engine / GKE |
| **Cloud Logging** | Monitoring & logging | - |
| **Identity Platform** | Authentication | Firebase Auth |

---

## ✨ Core Features & Rules

### System Rules & Prompts

The chatbot follows these core rules and system prompts:

#### 1. Main System Prompt (Configurable per Library)

```python
SYSTEM_PROMPT = """You are an expert assistant specializing in rights, legal information, and documentation, working for weknowrights.CA. 

CORE RULES:
1. Answer questions based ONLY on the provided context from documents
2. If the context doesn't contain sufficient information, clearly state: "I don't have information about that in the provided documents"
3. Always cite your sources with [Source: filename, Page: X] format
4. Be clear, accurate, and professional in all responses
5. Use bullet points for lists when appropriate
6. Maintain factual accuracy - never make up information
7. If asked about procedures or legal matters, emphasize following proper protocols
8. Provide comprehensive answers while remaining concise

CONTEXT:
{context}

HISTORY:
{history}

QUESTION: {question}

ANSWER:"""
```

#### 2. Summarization Prompt (for Chat Titles)

```python
SUMMARY_SYSTEM_PROMPT = """You are an expert at summarizing text down to exactly 4 words. 
Extract the most important 4 words that capture the essence of the text.

Text: {text}

4-word summary:"""
```

#### 3. Image Analysis Prompt (if processing images)

```python
IMAGE_SYSTEM_PROMPT = """You are an expert document analyst specialized in extracting comprehensive information from images for semantic search and retrieval.

CRITICAL REQUIREMENTS:

For CHARTS AND GRAPHS:
- Extract ALL data points, values, labels, and legends exactly as shown
- Capture complete axis information, scales, units, and numerical ranges
- Include ALL numerical values visible in the chart or graph
- Describe trends, patterns, and relationships shown in the data
- Preserve exact numerical data for searchability

For LEGAL DOCUMENTS AND FORMS:
- Extract ALL text content comprehensively and accurately
- Identify and describe key visual elements and their relationships
- Capture all visible text content including fine print
- Structure information for optimal search retrieval

For ALL IMAGES:
- Extract and preserve headlines, titles, and headings exactly as written
- Capture all visible text content comprehensively and accurately
- Use precise terminology when appropriate
- Ensure completeness over brevity - capture everything visible

Focus on factual accuracy, completeness, and optimal semantic search compatibility."""
```

### Core Features

| Feature | Description |
|---------|-------------|
| **RAG Chat** | Question answering with document context |
| **Streaming Responses** | Real-time token-by-token responses |
| **Citation Tracking** | Source references with page numbers |
| **Multi-Library Support** | Multiple document collections |
| **Chat History** | Persistent conversation storage |
| **User Feedback** | Thumbs up/down on responses |
| **Auto-Summarization** | Automatic chat title generation (4 words) |
| **Parent-Child Retrieval** | Optimized chunking strategy |

### Analytics Features

| Feature | Description |
|---------|-------------|
| **Unique Users by Day** | Daily active user tracking |
| **Messages by Day** | Usage statistics |
| **Feedback Percentages** | Response quality metrics |
| **Confidence Levels** | High/Medium/Low confidence tracking |
| **Citation Analytics** | Most cited documents |

---

## 🔬 Embedding Models & AI Configuration

### Embedding Models

#### Primary: text-embedding-ada-002 (OpenAI)
- **Dimensions**: 1536
- **Provider**: OpenAI / Vertex AI (if available)
- **Use Case**: Text embeddings for vector search
- **API Endpoint**: `https://api.openai.com/v1/embeddings` or Vertex AI equivalent

#### Alternative: text-embedding-004 (Google)
- **Dimensions**: 768 (base) or 1536 (large)
- **Provider**: Vertex AI
- **Use Case**: Google-native embeddings
- **API Endpoint**: Vertex AI Embeddings API

#### Configuration

```python
# Embedding Configuration
EMBEDDING_MODEL = "text-embedding-ada-002"  # or "text-embedding-004"
EMBEDDING_DIMENSION = 1536
EMBEDDING_API_VERSION = "2024-02-01"  # or Vertex AI version
```

### LLM Models

#### Primary: GPT-4o (OpenAI via Vertex AI or direct)
- **Model**: `gpt-4o` or `gpt-4-turbo`
- **Temperature**: 0.2 (for factual responses)
- **Max Tokens**: 1000-2000
- **Use Case**: Main chat responses

#### Alternative: Gemini Pro (Google)
- **Model**: `gemini-pro` or `gemini-1.5-pro`
- **Temperature**: 0.2-0.3
- **Max Tokens**: 1000-2000
- **Use Case**: Google-native chat responses

### Chunking Configuration

```python
# Parent-Child Chunking Strategy
PARENT_CHUNK_SIZE = 2000        # tokens
PARENT_CHUNK_OVERLAP = 200      # tokens
CHILD_CHUNK_SIZE = 500          # tokens
CHILD_CHUNK_OVERLAP = 50        # tokens

# Retrieval Configuration
RETURN_CHUNKS = 6               # Number of child chunks to retrieve
KNN_NEIGHBORS = 5               # K-nearest neighbors for vector search
```

### RAG Pipeline Parameters

```python
# RAG Optimization Settings
TEMPERATURE = 0.2               # Low for factual responses
MAX_TOKENS = 1000              # Response length limit
TOP_P = None                    # Nucleus sampling (optional)
FREQUENCY_PENALTY = None        # Reduce repetition (optional)
PRESENCE_PENALTY = None         # Encourage new topics (optional)
```

---

## 📁 Project Structure

```
weknowrights-ca-chatbot/
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py           # Configuration management
│   │   │
│   │   ├── models/                   # Pydantic data models
│   │   │   ├── __init__.py
│   │   │   ├── models.py             # General models (Health, AppConfig)
│   │   │   ├── chat_models.py        # Chat-related models
│   │   │   └── cognitive_models.py   # RAG request/response models
│   │   │
│   │   ├── services/                 # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication service (GCP Identity)
│   │   │   ├── cognitive_service.py  # RAG pipeline service
│   │   │   ├── llm_service.py        # LLM connection manager (Vertex AI)
│   │   │   ├── search_service_pc.py  # Parent-child retriever
│   │   │   ├── data_access.py        # Firestore operations
│   │   │   ├── docs.py               # Document library service
│   │   │   └── history_service.py    # Chat history formatting
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py            # Logging configuration
│   │       └── callbacks.py          # Streaming callbacks
│   │
│   ├── config/                       # Configuration files
│   │   ├── app_config.json           # Application settings
│   │   └── document_library_config.json  # Library configurations
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── env.template                  # Environment variable template
│   ├── start_server.ps1              # Local startup script
│   └── Dockerfile                    # Container definition
│
├── frontend/                         # Angular Frontend
│   └── frontend_generated/
│       ├── src/
│       │   ├── app/                  # Angular components
│       │   └── environments/         # Environment configs
│       ├── package.json
│       └── angular.json
│
├── embedding/                        # Document embedding tools
│   └── vertex-embedding/
│       ├── embed/
│       │   ├── embed_text.py         # Text embedding script
│       │   └── embed_images.py       # Image embedding script
│       └── requirements.txt
│
└── infrastructure/                   # IaC (Terraform/Deployment Manager)
    ├── terraform/
    └── cloudbuild.yaml
```

---

## ☁️ GCP Services Setup

### Phase 1: Enable Required APIs

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage-component.googleapis.com \
  secretmanager.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  identitytoolkit.googleapis.com
```

### Phase 2: Create GCP Resources

#### 2.1 Vertex AI Setup

```bash
# Create Vertex AI endpoint (if needed)
# Note: Vertex AI is regional, choose your region
gcloud ai models list --region=us-central1

# For embeddings, you'll use:
# - text-embedding-004 (Vertex AI)
# - Or text-embedding-ada-002 via OpenAI API
```

#### 2.2 Firestore Database

```bash
# Create Firestore database (Native mode)
gcloud firestore databases create \
  --location=us-central \
  --type=firestore-native

# Or use Firestore in Datastore mode
gcloud firestore databases create \
  --location=us-central \
  --type=datastore-mode
```

#### 2.3 Cloud Storage

```bash
# Create storage bucket for documents
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://weknowrights-documents

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://weknowrights-documents
```

#### 2.4 Secret Manager

```bash
# Create secrets
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-vertex-ai-key" | gcloud secrets create vertex-ai-key --data-file=-
```

#### 2.5 Identity Platform (Authentication)

```bash
# Enable Identity Platform
gcloud services enable identitytoolkit.googleapis.com

# Configure in GCP Console:
# - Go to Identity Platform
# - Enable Email/Password or OAuth providers
```

### Phase 3: Create Vector Search Index

For Vertex AI Vector Search, create an index:

```python
# Using Vertex AI Vector Search API
from google.cloud import aiplatform_v1

# Index configuration
index_config = {
    "dimensions": 1536,
    "approximate_neighbors_count": 10,
    "distance_measure_type": "DOT_PRODUCT_DISTANCE",
    "algorithm_config": {
        "tree_ah_config": {
            "leaf_node_embedding_count": 500,
            "leaf_nodes_to_search_percent": 10
        }
    }
}
```

---

## 💻 Backend Implementation

### 1. Environment Configuration

**backend/env.template**:

```bash
# Application
ENABLE_DOCS=1
SKIP_AUTH=0
LOG_LEVEL=INFO

# GCP Project
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1

# Firestore
FIRESTORE_DATABASE=weknowrights-chatbot
FIRESTORE_COLLECTION_CHATS=chats

# Vertex AI / OpenAI
OPENAI_API_KEY=your-openai-key  # Or use Secret Manager
VERTEX_AI_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.2

# Vector Search
VECTOR_SEARCH_INDEX=weknowrights-index
VECTOR_SEARCH_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1

# Cloud Storage
STORAGE_BUCKET=weknowrights-documents

# Identity Platform
IDENTITY_PLATFORM_API_KEY=your-api-key
```

### 2. Document Library Configuration

**backend/config/document_library_config.json**:

```json
{
  "root": {
    "weknowrights-main": {
      "document_library_name": "WeKnowRights Main Library",
      "storage_bucket": "weknowrights-documents",
      "container": "main-documents",
      "FIRESTORE_COLLECTION": "chats",
      "ad_group": null,
      
      "VECTOR_SEARCH_INDEX": "weknowrights-index",
      "VECTOR_SEARCH_ENDPOINT": "https://us-central1-aiplatform.googleapis.com/v1",
      "EMBEDDING_MODEL": "text-embedding-ada-002",
      "EMBEDDING_DIMENSION": 1536,
      "VECTOR_SEARCH_KNN": 5,
      
      "LLM_PROVIDER": "openai",
      "LLM_MODEL": "gpt-4o",
      "LLM_ENDPOINT": "https://api.openai.com/v1",
      "LLM_TEMPERATURE": 0.2,
      "LLM_MAX_TOKENS": 1000,
      
      "RETURN_CHUNKS": 6,
      "MAX_CHAT_TITLE_WORD_COUNT": 4,
      "SYSTEM_PROMPT": "You are an expert assistant specializing in rights, legal information, and documentation, working for weknowrights.CA. Answer questions based ONLY on the provided context from documents. Always cite your sources with [Source: filename, Page: X] format. Be clear, accurate, and professional."
    },
    "sum": {
      "LLM_PROVIDER": "openai",
      "LLM_MODEL": "gpt-4o",
      "LLM_TEMPERATURE": 0.4,
      "SYSTEM_PROMPT": "You are an expert at summarizing text down to exactly 4 words. Extract the most important 4 words that capture the essence of the text."
    }
  }
}
```

### 3. Key Service Implementations

#### LLM Service (Vertex AI / OpenAI)

```python
# backend/app/services/llm_service.py
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from google.cloud import aiplatform

class LLMService:
    def __init__(self):
        self.connections = {}
    
    def get_llm(self, lib_id: str, streaming: bool = True):
        config = settings.get_doc_config(lib_id)
        
        if config.LLM_PROVIDER == "vertexai":
            return ChatVertexAI(
                model_name=config.LLM_MODEL,
                temperature=config.LLM_TEMPERATURE,
                streaming=streaming,
                project=settings.gcp_project_id,
                location=settings.gcp_region
            )
        else:  # OpenAI
            return ChatOpenAI(
                model=config.LLM_MODEL,
                temperature=config.LLM_TEMPERATURE,
                streaming=streaming,
                openai_api_key=settings.openai_api_key
            )
```

#### Vector Search Retriever

```python
# backend/app/services/search_service_pc.py
from google.cloud import aiplatform_v1
from langchain.schema.retriever import BaseRetriever

class ParentChildRetriever(BaseRetriever):
    def __init__(self, embedding_model, vector_search_index, ...):
        self._embedding_model = embedding_model
        self._vector_search_client = aiplatform_v1.MatchServiceClient()
        # ... initialization
    
    def get_embedding(self, text: str) -> List[float]:
        # Use Vertex AI or OpenAI embeddings
        if self._embedding_model.startswith("text-embedding-ada"):
            # OpenAI embeddings
            response = openai_client.embeddings.create(
                model=self._embedding_model,
                input=text
            )
        else:
            # Vertex AI embeddings
            response = vertexai_client.embeddings.create(
                model=self._embedding_model,
                input=text
            )
        return response.data[0].embedding
    
    def _get_relevant_documents(self, query: str):
        # 1. Generate embedding
        embedding = self.get_embedding(query)
        
        # 2. Search child chunks in Vector Search
        # 3. Get parent chunks
        # 4. Return combined documents
        ...
```

#### Firestore Data Access

```python
# backend/app/services/data_access.py
from google.cloud import firestore

class ChatService:
    def __init__(self):
        self.db = firestore.Client(project=settings.gcp_project_id)
    
    def save_chat(self, user_id: str, chat_data: dict):
        collection = self.db.collection(settings.firestore_collection)
        doc_ref = collection.document(chat_data['partitionKey'])
        doc_ref.set(chat_data)
    
    def get_chats(self, user_id: str):
        collection = self.db.collection(settings.firestore_collection)
        query = collection.where('id', '==', user_id)
        return [doc.to_dict() for doc in query.stream()]
```

---

## 🎨 Frontend Implementation

### Angular Configuration

**frontend/frontend_generated/environment.ts**:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  gcp: {
    projectId: 'your-project-id',
    identityPlatform: {
      apiKey: 'your-api-key',
      authDomain: 'your-project.firebaseapp.com'
    }
  }
};
```

### Authentication Service (GCP Identity Platform)

```typescript
// frontend/src/services/auth.service.ts
import { Injectable } from '@angular/core';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private auth: any;
  
  constructor() {
    const app = initializeApp(environment.gcp.identityPlatform);
    this.auth = getAuth(app);
  }
  
  async signIn(email: string, password: string): Promise<string> {
    const userCredential = await signInWithEmailAndPassword(
      this.auth, email, password
    );
    return await userCredential.user.getIdToken();
  }
}
```

### Chat Service with Streaming

```typescript
// frontend/src/services/chat.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  constructor(private http: HttpClient) {}
  
  streamChat(request: any): Observable<string> {
    return new Observable(observer => {
      const eventSource = new EventSource(
        `${environment.apiUrl}/cognitive/stream`,
        {
          headers: {
            'Authorization': `Bearer ${this.getToken()}`
          }
        }
      );
      
      eventSource.onmessage = (event) => {
        observer.next(event.data);
      };
      
      eventSource.onerror = (error) => {
        observer.error(error);
        eventSource.close();
      };
    });
  }
}
```

---

## ⚙️ Configuration

### System Prompt Template

The chatbot uses configurable system prompts. Here's the base template:

```python
BASE_SYSTEM_PROMPT = """You are an expert assistant specializing in rights, legal information, and documentation, working for weknowrights.CA.

CORE RULES:
1. Answer questions based ONLY on the provided context from documents
2. If the context doesn't contain sufficient information, clearly state: "I don't have information about that in the provided documents"
3. Always cite your sources with [Source: filename, Page: X] format
4. Be clear, accurate, and professional in all responses
5. Use bullet points for lists when appropriate
6. Maintain factual accuracy - never make up information
7. If asked about procedures or legal matters, emphasize following proper protocols
8. Provide comprehensive answers while remaining concise

Context:
{context}

Previous conversation:
{history}

Question: {question}

Answer:"""
```

### Chunking Strategy

```python
# Parent chunks: Large context windows
PARENT_CHUNK_SIZE = 2000        # tokens
PARENT_CHUNK_OVERLAP = 200      # tokens (10% overlap)

# Child chunks: Smaller, precise search units
CHILD_CHUNK_SIZE = 500          # tokens
CHILD_CHUNK_OVERLAP = 50        # tokens (10% overlap)
```

### Retrieval Parameters

```python
RETURN_CHUNKS = 6               # Number of child chunks to retrieve
KNN_NEIGHBORS = 5               # K-nearest neighbors for vector search
TEMPERATURE = 0.2               # Low temperature for factual responses
MAX_TOKENS = 1000               # Response length limit
```

---

## 🚀 Deployment

### Cloud Run Deployment

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/weknowrights-backend

gcloud run deploy weknowrights-backend \
  --image gcr.io/YOUR_PROJECT_ID/weknowrights-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID
```

### Frontend Deployment (Firebase Hosting)

```bash
# Build Angular app
cd frontend/frontend_generated
npm run build

# Deploy to Firebase
firebase deploy --only hosting
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔒 Security

### Authentication Flow

```
1. User logs in via GCP Identity Platform / Firebase Auth
2. Frontend gets ID token
3. Frontend sends token with each API request
4. Backend validates token with Identity Platform
5. If valid, process request
```

### Service Account & IAM

```bash
# Create service account
gcloud iam service-accounts create weknowrights-backend \
  --display-name="WeKnowRights Backend Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:weknowrights-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:weknowrights-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:weknowrights-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Secret Management

```python
# Use Secret Manager for sensitive data
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

---

## 📊 Monitoring & Logging

### Cloud Logging

```python
# backend/app/utils/logging.py
from google.cloud import logging as cloud_logging

client = cloud_logging.Client()
client.setup_logging()

import logging
logger = logging.getLogger(__name__)
logger.info("Application started")
```

### Key Metrics to Track

- Response latency
- Token usage
- Error rates
- User engagement
- Feedback scores
- Vector search performance

---

## 🎯 Best Practices

### RAG Optimization

1. **Chunk Size**: 500-1000 tokens for child chunks
2. **Overlap**: 10-20% overlap between chunks
3. **Parent Context**: Include 2000+ tokens for full context
4. **Top-K**: Start with k=5-10, tune based on quality
5. **Temperature**: Use 0.1-0.3 for factual responses

### Error Handling

- Graceful degradation when services fail
- Retry logic with exponential backoff
- Clear error messages for users
- Comprehensive logging for debugging

---

## 📚 Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Angular Documentation](https://angular.io/docs)

---

## 🔄 Migration from Azure to GCP

### Service Mapping

| Azure Service | GCP Equivalent |
|---------------|---------------|
| Azure OpenAI | Vertex AI (Gemini) or OpenAI API |
| Azure AI Search | Vertex AI Vector Search / Matching Engine |
| Azure Cosmos DB | Cloud Firestore / Cloud SQL |
| Azure Blob Storage | Cloud Storage |
| Azure Key Vault | Secret Manager |
| Azure App Service | Cloud Run / App Engine |
| Application Insights | Cloud Logging / Cloud Monitoring |
| Azure AD | Identity Platform / Firebase Auth |

### Key Code Changes

1. **Authentication**: Replace Azure AD with Identity Platform
2. **Database**: Replace Cosmos DB with Firestore
3. **Storage**: Replace Blob Storage with Cloud Storage
4. **Vector Search**: Replace Azure AI Search with Vertex AI Vector Search
5. **LLM**: Replace Azure OpenAI with Vertex AI or direct OpenAI API
6. **Secrets**: Replace Key Vault with Secret Manager

---

**Built with ❤️ for weknowrights.CA**

For questions or issues, please refer to the project documentation or contact the development team.

