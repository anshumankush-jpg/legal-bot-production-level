# PLAZA-AI Artillery Multi-Modal Embedding API
# Production-ready container with SentenceTransformers + CLIP + FAISS

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for document processing and OCR
RUN apt-get update && apt-get install -y \
    # OCR dependencies
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    # PDF processing
    libpoppler-cpp-dev \
    # Image processing
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Build tools
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r plaza && useradd -r -g plaza plaza

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install CLIP (must be done after torch installation)
RUN pip install git+https://github.com/openai/CLIP.git

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data/faiss /app/data/uploads /app/logs \
    && chown -R plaza:plaza /app

# Pre-download and cache models at build time for faster startup
RUN python -c "
import os
os.environ['HF_HOME'] = '/app/models'
os.environ['TORCH_HOME'] = '/app/models'

print('🚀 Pre-downloading SentenceTransformer model...')
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
print('✅ SentenceTransformer model cached')

print('🖼️ Pre-downloading CLIP model...')
import clip
clip_model, preprocess = clip.load('ViT-B/32', device='cpu')
print('✅ CLIP model cached')

print('🎯 Models ready for production!')
" || echo '⚠️ Model preloading failed, will download at runtime'

# Set proper permissions
RUN chown -R plaza:plaza /app

# Switch to non-root user
USER plaza

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "
import requests
import sys
try:
    response = requests.get('http://localhost:8000/api/artillery/health', timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'healthy':
            sys.exit(0)
    sys.exit(1)
except:
    sys.exit(1)
" || exit 1

# Expose port
EXPOSE 8000

# Default environment variables (can be overridden)
ENV GOOGLE_CLOUD_PROJECT=""
ENV GCS_BUCKET_NAME=""
ENV CLOUD_SQL_INSTANCE=""
ENV CLOUD_SQL_DATABASE="plaza_ai"
ENV EMBEDDING_MODEL="all-MiniLM-L6-v2"
ENV CLIP_MODEL="ViT-B/32"
ENV FAISS_DIMENSION="384"
ENV CHUNK_SIZE="1000"
ENV CHUNK_OVERLAP="200"

# Run the application
CMD ["python", "-m", "uvicorn", "api_server:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--http", "httptools", \
     "--access-log", \
     "--log-level", "info"]