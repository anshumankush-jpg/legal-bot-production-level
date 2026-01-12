# .env File Setup Guide

## 📁 Where to Put .env Files

You can create `.env` files in **two locations**:

1. **Root directory** (`PLAZA-AI/.env`) - For global settings
2. **Backend directory** (`PLAZA-AI/backend/.env`) - For backend-specific settings

The backend will look for `.env` in both locations (backend first, then root).

## 🚀 Quick Setup

### Step 1: Create .env File

**Option A: Copy the example file**
```bash
# In root directory
copy .env.example .env

# Or in backend directory
cd backend
copy .env.example .env
```

**Option B: Create manually**
Create a file named `.env` in the `backend` directory.

### Step 2: Add Your OpenAI API Key

Open `.env` and add:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### Step 3: Verify Configuration

The `.env.example` files already have the optimal settings:
- ✅ `OPENAI_CHAT_MODEL=gpt-4o-mini` (cheapest)
- ✅ `OPENAI_EMBEDDING_MODEL=text-embedding-ada-002`
- ✅ `EMBEDDING_PROVIDER=openai` (since sentence_transformers not working)
- ✅ `LLM_PROVIDER=openai`

## 📋 Minimum Required Settings

For the system to work with OpenAI, you only need:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
```

Everything else has sensible defaults!

## 🔍 Check Your Setup

After creating `.env`, test it:

```bash
python check_openai_balance.py
```

This will verify:
- ✅ API key is set
- ✅ API key works
- ✅ Current configuration
- ✅ Pricing information

## 💡 Tips

1. **Never commit .env to git** - It contains secrets!
2. **Use .env.example** as a template
3. **Backend directory .env takes precedence** over root .env
4. **Restart backend** after changing .env

## 📝 Example .env File

```env
# Minimum required for OpenAI
OPENAI_API_KEY=sk-proj-abc123...
OPENAI_CHAT_MODEL=gpt-4o-mini
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai

# Optional: Free alternatives
# LLM_PROVIDER=ollama  # 100% free, no API key needed!
# OLLAMA_MODEL=llama3.2
```

## 🆘 Troubleshooting

**"OPENAI_API_KEY not found"**
- Make sure `.env` file exists in `backend/` directory
- Check the key starts with `sk-`
- Restart backend after adding key

**"API key test failed"**
- Verify key is valid at https://platform.openai.com/api-keys
- Check you have credits in your account
- Make sure key has proper permissions

**Settings not applying**
- Restart backend after changing .env
- Check backend directory .env (takes precedence)
- Verify no typos in variable names

---

**Ready?** Create your `.env` file and run `python check_openai_balance.py`! 🚀
