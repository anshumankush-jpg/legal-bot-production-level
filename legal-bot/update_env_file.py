"""
Update .env file with optimal settings for OpenAI
"""
import os
from pathlib import Path

def update_env_file():
    """Update .env file with optimal settings."""
    env_path = Path("backend/.env")
    
    # Read existing .env if it exists
    existing_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key] = value
    
    # Preserve API key if it exists
    api_key = existing_vars.get('OPENAI_API_KEY', 'sk-your-openai-api-key-here')
    
    # Optimal configuration
    env_content = f"""# PLAZA-AI Backend Environment Configuration
# Updated with optimal settings for OpenAI

# ============================================
# OpenAI Configuration (Required)
# ============================================
OPENAI_API_KEY={api_key}

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
    
    # Write to .env file
    env_path.parent.mkdir(parents=True, exist_ok=True)
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"[OK] Updated {env_path}")
    print(f"[INFO] API Key: {api_key[:20]}...")
    print(f"[INFO] Model: gpt-4o-mini (cheapest)")
    print(f"[INFO] Embedding: OpenAI")
    print("\n[NOTE] Make sure to add your actual OpenAI API key if not already set!")

if __name__ == "__main__":
    update_env_file()
