"""
Simple script to append OAuth credentials to .env file.
Preserves existing content and adds new OAuth settings.
"""
from pathlib import Path

def add_oauth_config():
    """Add OAuth credentials to .env file."""
    
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("[ERROR] .env file not found!")
        return
    
    # Read existing content
    with open(env_path, 'r') as f:
        existing_content = f.read()
    
    # Check if already added
    if "GOOGLE_CLIENT_ID=1086283983680" in existing_content:
        print("[INFO] OAuth configuration already exists!")
        print("[INFO] Your .env file is ready.")
        print("\n[ACTION] Just add your Google Client Secret where it says:")
        print("GOOGLE_CLIENT_SECRET=REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE")
        return
    
    # OAuth configuration to append
    oauth_config = """

# ============================================
# JWT Authentication Configuration
# ============================================
JWT_SECRET_KEY=Jni3sMACf40fCHm8h-K14jTWV_Vkii-M3fCjbpk4C-klK8dv1Zai-FakYlFpX6kgmC_XRcJteGYy27KA4BGGqA
JWT_ACCESS_TTL_MIN=30
JWT_REFRESH_TTL_DAYS=30

# ============================================
# Frontend Configuration
# ============================================
FRONTEND_BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:5173

# ============================================
# Google OAuth Configuration (User Authentication)
# ============================================
GOOGLE_CLIENT_ID=1086283983680-m0rg0loe9ktg0vd4rv5onmarr8lgpqbu.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google

# ============================================
# Database Configuration
# ============================================
DATABASE_URL=sqlite:///./data/legal_bot.db
"""
    
    # Append to file
    with open(env_path, 'a') as f:
        f.write(oauth_config)
    
    print("[OK] OAuth configuration added to .env file!")
    print("\n[NEXT STEP]")
    print("Edit backend/.env and find this line:")
    print("GOOGLE_CLIENT_SECRET=REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE")
    print("\nReplace it with your actual Client Secret from Google Cloud Console")
    print("(It looks like: GOCSPX-xxxxxxxxxxxxx)")

if __name__ == "__main__":
    add_oauth_config()
