# ⚡ Quick Start Guide

Get up and running in 5 minutes!

---

## 🚀 Step 1: Install

```bash
pip install -r requirements.txt
```

**Optional** (for image embedding):
```bash
pip install git+https://github.com/openai/CLIP.git
```

---

## 🧪 Step 2: Test

```bash
python test_server.py
```

Should see: `✅ All tests passed!`

---

## 🎯 Step 3: Use It!

### Option A: Python Library

```python
from unified_embedding_server import UnifiedEmbeddingServer, EmbeddingRequest

# Create server
server = UnifiedEmbeddingServer()

# Embed text
response = server.embed(EmbeddingRequest(
    content="AI is transforming healthcare",
    content_type="text"
))

print(f"Embedded! Dimension: {len(response.embeddings[0])}")
```

### Option B: API Server

**Terminal 1:**
```bash
python api_server.py
```

**Terminal 2:**
```bash
python client_example.py
```

Or visit: http://localhost:8000/docs

---

## 📚 Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🏗️ See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- 💻 Check [example_usage.py](example_usage.py) for more examples

---

## 🎉 That's It!

You're ready to embed text, images, tables, and documents! 🚀

