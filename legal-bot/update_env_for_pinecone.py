"""Helper script to update .env file with Pinecone and Meilisearch configuration."""
import os
from pathlib import Path

def update_env_file():
    """Update backend/.env file with Pinecone configuration."""
    env_path = Path("backend/.env")
    
    if not env_path.exists():
        print("[X] backend/.env file not found!")
        print("   Creating a new one...")
        create_new_env = True
    else:
        create_new_env = False
        print(f"[OK] Found .env file at: {env_path}")
    
    # Read existing env if it exists
    env_lines = []
    existing_keys = set()
    
    if not create_new_env:
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
        
        # Parse existing keys
        for line in env_lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                existing_keys.add(key)
    
    # New configuration to add
    new_config = {
        'VECTOR_STORE': 'pinecone',
        'EMBEDDING_DIMENSIONS': '1536',
        'PINECONE_API_KEY': 'pcsk_32Scji_ES7HgKskDQVdeHmcNBVaoUPJVikvqoAdj7jmjQrDtrMe6DAzWUmipY4B4wQPfr3',
        'PINECONE_ENVIRONMENT': 'us-east-1',
        'PINECONE_INDEX_NAME': 'legal-docs',
        'USE_PINECONE': 'true',
        'USE_MEILISEARCH': 'false',
        'MEILISEARCH_HOST': 'http://localhost:7700',
        'MEILISEARCH_API_KEY': '',
        'MEILISEARCH_INDEX_NAME': 'legal-documents'
    }
    
    # Update or add new keys
    updated_lines = []
    keys_added = set()
    
    for line in env_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            key = stripped.split('=')[0].strip()
            if key in new_config:
                # Update this key
                updated_lines.append(f"{key}={new_config[key]}\n")
                keys_added.add(key)
                print(f"[Updated] {key}")
            else:
                # Keep existing line
                updated_lines.append(line)
        else:
            # Keep comments and empty lines
            updated_lines.append(line)
    
    # Add new keys that weren't in the file
    if keys_added != set(new_config.keys()):
        updated_lines.append("\n# Pinecone and Meilisearch Configuration (Added automatically)\n")
        for key, value in new_config.items():
            if key not in keys_added:
                updated_lines.append(f"{key}={value}\n")
                print(f"[Added] {key}")
    
    # Write updated file
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"\n[SUCCESS] Updated {env_path}")
    print("\n" + "="*80)
    print("CONFIGURATION SUMMARY")
    print("="*80)
    print(f"Vector Store: Pinecone (cloud)")
    print(f"Index Name: {new_config['PINECONE_INDEX_NAME']}")
    print(f"Environment: {new_config['PINECONE_ENVIRONMENT']}")
    print(f"Embedding Dimension: {new_config['EMBEDDING_DIMENSIONS']}")
    print(f"Meilisearch: {'Enabled' if new_config['USE_MEILISEARCH'] == 'true' else 'Disabled'}")
    print("="*80)
    
    print("\n[WARNING] SECURITY NOTE:")
    print("Your Pinecone API key was shared in chat. Consider regenerating it at:")
    print("https://app.pinecone.io/")
    print("\n[NEXT STEPS]")
    print("1. Test the integration: cd backend && python test_pinecone_integration.py")
    print("2. If test passes, restart your backend")
    print("3. Re-ingest documents: python ingest_all_documents.py")
    print("4. (Optional) Start Meilisearch for keyword search")


if __name__ == "__main__":
    print("="*80)
    print("UPDATING .ENV FILE FOR PINECONE + MEILISEARCH")
    print("="*80 + "\n")
    
    try:
        update_env_file()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
