# How to Create .env Files

## 📋 Quick Steps

### Step 1: Create .env in Backend Directory

**Windows (PowerShell):**
```powershell
cd backend
Copy-Item env_template.txt .env
notepad .env
```

**Windows (Command Prompt):**
```cmd
cd backend
copy env_template.txt .env
notepad .env
```

**Mac/Linux:**
```bash
cd backend
cp env_template.txt .env
nano .env
```

### Step 2: Add Your OpenAI API Key

Open the `.env` file and replace:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

With your actual key:
```env
OPENAI_API_KEY=sk-proj-abc123xyz...
```

Get your API key from: https://platform.openai.com/api-keys

### Step 3: Verify

The template already has optimal settings:
- ✅ `OPENAI_CHAT_MODEL=gpt-4o-mini` (cheapest)
- ✅ `EMBEDDING_PROVIDER=openai` (since sentence_transformers not working)
- ✅ `LLM_PROVIDER=openai`

### Step 4: Test

```bash
python check_openai_balance.py
```

## 📁 File Locations

You can create `.env` files in:

1. **`backend/.env`** (recommended - backend-specific)
2. **`.env`** (root directory - global)

Backend directory `.env` takes precedence.

## ✅ Minimum Required

For the system to work, you only need:

```env
OPENAI_API_KEY=sk-your-key-here
```

Everything else has defaults!

## 🎯 What's Already Configured

The template includes:
- ✅ GPT-4o-mini (cheapest model - 94% savings)
- ✅ OpenAI embeddings (since sentence_transformers not working)
- ✅ Optimal token limits
- ✅ Free provider options (commented out)

## 🚀 Next Steps

1. Create `.env` file from template
2. Add your OpenAI API key
3. Run `python check_openai_balance.py` to verify
4. Restart backend

That's it! 🎉
