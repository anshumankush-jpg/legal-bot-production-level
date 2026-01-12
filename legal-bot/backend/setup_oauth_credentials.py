"""
Script to add OAuth credentials to .env file.
Run this to configure Google and Microsoft OAuth.
"""
import os
from pathlib import Path

def setup_oauth_credentials():
    """Add OAuth credentials to .env file."""
    env_path = Path(__file__).parent / ".env"
    
    # Read existing .env
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    else:
        existing_content = ""
    
    # OAuth credentials to add
    oauth_vars = {
        'GOOGLE_CLIENT_ID': '1086283983680-cnmfcbrv2d8hhc047llkog1nkhbu01tm.apps.googleusercontent.com',
        'GOOGLE_CLIENT_SECRET': 'GOCSPX-your-secret-here',  # You need to add the actual secret
        'GOOGLE_REDIRECT_URI': 'http://localhost:4200/auth/callback/google',
        'MS_CLIENT_ID': 'your-microsoft-client-id',  # Add your Microsoft client ID
        'MS_CLIENT_SECRET': 'your-microsoft-secret',  # Add your Microsoft secret
        'MS_TENANT': 'common',
        'MS_REDIRECT_URI': 'http://localhost:4200/auth/callback/microsoft',
    }
    
    # Check which vars are missing
    lines_to_add = []
    for key, value in oauth_vars.items():
        if key not in existing_content:
            lines_to_add.append(f"{key}={value}")
            print(f"[+] Adding {key}")
        else:
            print(f"[*] {key} already exists")
    
    if lines_to_add:
        # Add OAuth section
        oauth_section = "\n\n# OAuth Configuration\n" + "\n".join(lines_to_add)
        
        with open(env_path, 'a', encoding='utf-8') as f:
            f.write(oauth_section)
        
        print(f"\n[OK] Added {len(lines_to_add)} OAuth variables to .env")
        print("\n[!] IMPORTANT: Update these values with your actual credentials:")
        print("   - GOOGLE_CLIENT_SECRET")
        print("   - MS_CLIENT_ID")
        print("   - MS_CLIENT_SECRET")
    else:
        print("\n[OK] All OAuth variables already configured")
    
    print("\n[INFO] Current OAuth Configuration:")
    print("-" * 60)
    for key in oauth_vars.keys():
        value = os.getenv(key, "NOT SET")
        # Mask secrets
        if 'SECRET' in key and value != "NOT SET":
            value = value[:10] + "..." if len(value) > 10 else "***"
        print(f"{key}: {value}")

if __name__ == "__main__":
    setup_oauth_credentials()
