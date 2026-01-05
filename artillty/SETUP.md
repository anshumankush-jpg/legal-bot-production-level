# 🚀 Setup Guide

## Quick Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install CLIP (Optional, for Image Embedding)

```bash
pip install git+https://github.com/openai/CLIP.git
```

**Note**: CLIP is optional. The server works without it, but image embedding will be disabled.

### Step 3: Verify Installation

```bash
python test_server.py
```

All tests should pass! ✅

---

## Running the Server

### Option 1: API Server (Recommended)

```bash
python api_server.py
```

Then visit:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

### Option 2: Python Library

```python
from unified_embedding_server import UnifiedEmbeddingServer, EmbeddingRequest

server = UnifiedEmbeddingServer()
# Use as shown in examples
```

### Option 3: Run Examples

```bash
python example_usage.py
```

---

## First-Time Setup Notes

### Model Downloads

On first run, the following models will be downloaded automatically:

1. **SentenceTransformer** (~80MB)
   - Model: `all-MiniLM-L6-v2`
   - Location: `~/.cache/huggingface/`

2. **CLIP** (~150MB, if installed)
   - Model: `ViT-B/32`
   - Location: `~/.cache/torch/`

**Total download**: ~230MB on first run

### System Requirements

- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 1GB free space (for models)
- **CPU**: Any modern CPU works
- **GPU**: Optional (CUDA for faster processing)

---

## Troubleshooting

### Issue: "No module named 'clip'"

**Solution**: Install CLIP separately:
```bash
pip install git+https://github.com/openai/CLIP.git
```

Or skip image embedding (server works without CLIP).

### Issue: "CUDA out of memory"

**Solution**: Use CPU mode:
```python
server = UnifiedEmbeddingServer(device="cpu")
```

### Issue: "Model download fails"

**Solution**: 
1. Check internet connection
2. Models are cached in `~/.cache/huggingface/`
3. Try downloading manually from HuggingFace

### Issue: "PDF extraction fails"

**Solution**: Ensure all dependencies are installed:
```bash
pip install pdfplumber pypdf2
```

---

## Production Deployment

### Using Docker (Coming Soon)

```bash
docker build -t embedding-server .
docker run -p 8000:8000 embedding-server
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Environment Variables

```bash
export EMBEDDING_DEVICE=cuda  # or cpu
export EMBEDDING_TEXT_MODEL=all-MiniLM-L6-v2
export EMBEDDING_IMAGE_MODEL=ViT-B/32
```

---

## Next Steps

1. ✅ Installation complete
2. 📖 Read [README.md](README.md) for usage examples
3. 🧪 Run `python test_server.py` to verify
4. 🚀 Start building with `python api_server.py`

---

**Ready to embed! 🎉**

