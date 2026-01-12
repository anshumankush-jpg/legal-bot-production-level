"""Fix OAuth redirect URI to match current frontend port (4200)."""
import os
from pathlib import Path

def fix_redirect_uri():
    """Update redirect URI from 5173 to 4200."""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("[ERROR] .env file not found")
        return
    
    # Read .env
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace old port with new port
    updated_content = content.replace(
        'http://localhost:5173/',
        'http://localhost:4200/'
    )
    
    # Write back
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("[OK] Redirect URI updated to http://localhost:4200")
    print("[INFO] Please update Google Cloud Console:")
    print("  1. Go to: https://console.cloud.google.com/apis/credentials")
    print("  2. Edit your OAuth 2.0 Client ID")
    print("  3. Add authorized redirect URI: http://localhost:4200/auth/callback/google")
    print("  4. Save changes")
    print("\n[INFO] Restart backend for changes to take effect")

if __name__ == "__main__":
    fix_redirect_uri()
