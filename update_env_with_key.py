"""
Update backend/.env file with OpenAI API key
"""
import os
from pathlib import Path

# Your OpenAI API key
API_KEY = "your-openai-api-key-here"

# Path to .env file
env_path = Path("backend/.env")

# Create .env content
env_content = f"""# PLAZA-AI Backend Environment Configuration
# Updated with OpenAI API key

# ============================================
# OpenAI Configuration (Required)
# ============================================
OPENAI_API_KEY={API_KEY}

# Chat Model (gpt-4o-mini is cheapest - 94% savings!)
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
OPENAI_MAX_TOKENS=1500

# Embedding Model
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# ============================================
# LLM Provider Selection
# ============================================
LLM_PROVIDER=openai

# ============================================
# Embedding Provider Selection
# ============================================
EMBEDDING_PROVIDER=openai

# ============================================
# Server Configuration
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=False
"""

# Write to file
env_path.parent.mkdir(parents=True, exist_ok=True)
with open(env_path, 'w') as f:
    f.write(env_content)

print(f"[SUCCESS] Updated {env_path}")
print(f"[INFO] API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"[INFO] Model: gpt-4o-mini")
print(f"[INFO] Embedding: OpenAI")
print("\n[OK] .env file is ready!")
