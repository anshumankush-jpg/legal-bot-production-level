"""Setup OAuth environment variables for LegalAI."""
import os
from pathlib import Path

def setup_oauth_env():
    """Add OAuth configuration to .env file."""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    # OAuth configuration
    oauth_config = """
# ============================================
# Google OAuth Configuration (User Authentication)
# ============================================
GOOGLE_CLIENT_ID=1086283983680-cnmfcbrv2d8hhc047llkog1nkhbu01tm.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=http://localhost:4200/auth/callback/google

# ============================================
# Microsoft OAuth Configuration
# ============================================
# MS_CLIENT_ID=your-microsoft-client-id
# MS_CLIENT_SECRET=your-microsoft-client-secret
# MS_TENANT=common
# MS_REDIRECT_URI=http://localhost:4200/auth/callback/microsoft

# ============================================
# JWT Configuration
# ============================================
JWT_SECRET_KEY=dev-secret-key-change-in-production-use-openssl-rand-hex-32
JWT_ACCESS_TTL_MIN=1440
JWT_REFRESH_TTL_DAYS=30

# ============================================
# Environment
# ============================================
ENVIRONMENT=dev
BASE_URL=http://localhost:4200
"""
    
    # Read existing .env if it exists
    existing_content = ""
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # Check if OAuth config already exists
    if "GOOGLE_CLIENT_ID" in existing_content and "1086283983680-cnmfcbrv2d8hhc047llkog1nkhbu01tm" in existing_content:
        print("[OK] OAuth configuration already exists in .env")
        return
    
    # Remove old OAuth config if exists
    lines = existing_content.split('\n')
    filtered_lines = []
    skip_section = False
    
    for line in lines:
        if 'Google OAuth Configuration' in line or 'Microsoft OAuth Configuration' in line:
            skip_section = True
            continue
        if skip_section and line.startswith('#'):
            continue
        if skip_section and (line.startswith('GOOGLE_') or line.startswith('MS_') or line.startswith('JWT_') or line.startswith('ENVIRONMENT') or line.startswith('BASE_URL')):
            continue
        if skip_section and line.strip() == '':
            skip_section = False
            continue
        filtered_lines.append(line)
    
    # Write updated .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(filtered_lines))
        f.write('\n')
        f.write(oauth_config)
    
    print("[OK] OAuth configuration added to .env")
    print(f"[INFO] File location: {env_file}")
    print("\n[NEXT STEPS]:")
    print("1. Update Google Cloud Console redirect URIs:")
    print("   - Add: http://localhost:4200/auth/callback/google")
    print("2. For Microsoft OAuth, add your credentials to .env")
    print("3. Restart the backend server")

if __name__ == "__main__":
    setup_oauth_env()
