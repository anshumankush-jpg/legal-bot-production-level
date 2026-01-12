# Free LLM Setup Guide for PLAZA-AI

This guide shows you how to use **100% FREE** LLM providers with PLAZA-AI.

## 🎯 Best Free Options (Ranked)

### 1. **Ollama** ⭐ RECOMMENDED (100% Free, Local, NO API KEY NEEDED!)
- **Cost**: $0 (runs on your computer)
- **API Key**: ❌ **NONE REQUIRED** - Works completely offline!
- **Speed**: Fast (local processing)
- **Privacy**: 100% private (no data sent to cloud)
- **Setup**: Easy (5 minutes)

### 2. **Google Gemini** (Free Tier)
- **Cost**: Free tier: 15 requests/minute, 1M tokens/day
- **API Key**: ✅ **REQUIRED** (but free to get at https://makersuite.google.com/app/apikey)
- **Speed**: Very fast (cloud-based)
- **Privacy**: Data sent to Google
- **Setup**: Easy (2 minutes)

### 3. **Hugging Face Inference API** (Free Tier)
- **Cost**: Free tier with limited requests
- **API Key**: ✅ **REQUIRED** (but free to get at https://huggingface.co/settings/tokens)
- **Speed**: Fast (cloud-based)
- **Privacy**: Data sent to Hugging Face
- **Setup**: Easy (2 minutes)

---

## 🚀 Quick Start: Ollama (Recommended)

### Step 1: Install Ollama

**Windows:**
```bash
# Download from https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama
```

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download a Model

```bash
# Fast, small model (recommended for speed)
ollama pull llama3.2

# Or larger, more capable model
ollama pull mistral
ollama pull phi3
```

### Step 3: Configure PLAZA-AI

Add to your `.env` file:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Step 4: Start Ollama

```bash
# Ollama runs automatically after installation
# Verify it's running:
ollama list
```

### Step 5: Test

Restart your backend and ask a question. Ollama will process it locally!

---

## 🌟 Google Gemini Setup (Free Tier)

### Step 1: Get API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### Step 2: Configure

Add to your `.env` file:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### Step 3: Test

Restart backend and test!

**Free Tier Limits:**
- 15 requests per minute
- 1 million tokens per day
- Perfect for development and light usage

---

## 🤗 Hugging Face Setup (Free Tier)

### Step 1: Get API Key

1. Go to https://huggingface.co/settings/tokens
2. Sign up/login
3. Create a new token (read access)
4. Copy the token

### Step 2: Configure

Add to your `.env` file:
```env
LLM_PROVIDER=huggingface
HUGGINGFACE_API_KEY=your_token_here
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### Step 3: Test

Restart backend and test!

**Free Models Available:**
- `mistralai/Mistral-7B-Instruct-v0.2`
- `meta-llama/Llama-2-7b-chat-hf`
- `google/flan-t5-large`

---

## 📊 Comparison

| Provider | Cost | API Key Needed? | Speed | Privacy | Setup Time |
|----------|------|-----------------|-------|---------|------------|
| **Ollama** | $0 | ❌ **NO** | ⚡⚡⚡ Fast | 🔒 100% Private | 5 min |
| **Gemini** | Free tier | ✅ Yes (free) | ⚡⚡⚡⚡ Very Fast | ☁️ Cloud | 2 min |
| **Hugging Face** | Free tier | ✅ Yes (free) | ⚡⚡ Fast | ☁️ Cloud | 2 min |

---

## 🔧 Auto-Detection

If you don't set `LLM_PROVIDER`, the system will automatically try:
1. **Ollama** (if running locally)
2. **Gemini** (if API key is set)
3. **Hugging Face** (if API key is set)
4. **OpenAI/Azure** (if configured, paid)

---

## 💡 Tips

### For Best Performance:
- **Use Ollama** for development (100% free, fast, private)
- **Use Gemini** for production (if within free tier limits)
- **Use Ollama** if you have a good GPU (even faster)

### For Privacy:
- **Ollama** is the only 100% private option (runs locally)
- All other options send data to cloud providers

### For Speed:
- **Gemini** is fastest (cloud infrastructure)
- **Ollama** is fast if you have GPU
- **Hugging Face** depends on model and load

---

## 🐛 Troubleshooting

### Ollama Not Working?
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Test a model
ollama run llama3.2 "Hello, how are you?"
```

### Gemini Rate Limits?
- Free tier: 15 requests/minute
- If you hit limits, wait 1 minute or use Ollama

### Hugging Face Errors?
- Some models require accepting terms on Hugging Face website
- Check model page: https://huggingface.co/{model_name}
- Click "Agree and access repository"

---

## 📝 Environment Variables Summary

```env
# Choose one provider:
LLM_PROVIDER=ollama          # or gemini, huggingface, openai, azure

# Ollama (if using)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Gemini (if using)
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash

# Hugging Face (if using)
HUGGINGFACE_API_KEY=your_token_here
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

---

## ✅ Next Steps

1. **Choose a provider** (Ollama recommended for 100% free)
2. **Follow setup steps** above
3. **Update `.env` file**
4. **Restart backend**
5. **Test with a legal question!**

Enjoy your **FREE** legal AI assistant! 🎉
