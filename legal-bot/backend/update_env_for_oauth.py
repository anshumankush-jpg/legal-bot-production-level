"""
Script to add OAuth credentials to existing .env file.
This preserves your existing OpenAI key and adds new OAuth settings.
"""
import os
from pathlib import Path

def update_env_file():
    """Add OAuth credentials to .env file."""
    
    env_path = Path(__file__).parent / ".env"
    
    # Read existing content
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_content = f.read()
    else:
        print("[ERROR] .env file not found!")
        return
    
    # OAuth configuration to add
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
# Microsoft OAuth Configuration (Optional)
# ============================================
# MS_CLIENT_ID=your-microsoft-client-id
# MS_CLIENT_SECRET=your-microsoft-client-secret
# MS_TENANT=common
# MS_REDIRECT_URI=http://localhost:5173/auth/callback/microsoft

# ============================================
# Gmail OAuth Configuration (Optional - for employee email)
# ============================================
# GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
# GMAIL_CLIENT_SECRET=your-gmail-client-secret
# GMAIL_REDIRECT_URI=http://localhost:5173/employee/email/callback

# ============================================
# Database Configuration
# ============================================
DATABASE_URL=sqlite:///./data/legal_bot.db
"""
    
    # Check if OAuth config already exists
    if "GOOGLE_CLIENT_ID" in existing_content:
        print("[WARNING] OAuth configuration already exists in .env file")
        response = input("Do you want to overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Add OAuth config at the end
    updated_content = existing_content.rstrip() + "\n\n" + oauth_config
    
    # Write back
    with open(env_path, 'w') as f:
        f.write(updated_content)
    
    print("\n[OK] OAuth configuration added to .env file!")
    print("\n[ACTION REQUIRED]")
    print("   Replace 'REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE'")
    print("   with your actual Client Secret from Google Cloud Console")
    print("\n   The Client Secret looks like: GOCSPX-xxxxxxxxxxxxx")
    print("\n[OK] JWT Secret Key already generated and added!")
    print(f"   Key: Jni3sMACf40fCHm8h-K14jTWV_Vkii-M3fCjbpk4C-klK8dv1Zai-FakYlFpX6kgmC_XRcJteGYy27KA4BGGqA")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Adding OAuth Credentials to .env File")
    print("="*60 + "\n")
    
    update_env_file()
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("\n1. Get Client Secret from Google Cloud Console")
    print("2. Edit backend/.env and replace the placeholder")
    print("3. Save the file")
    print("4. Run: python -m alembic upgrade head")
    print("5. Run: python -m scripts.seed_demo_data")
    print("6. Start backend: python -m uvicorn app.main:app --reload --port 8000")
    print("7. Start frontend: cd ../frontend && npm run dev")
    print("\n")
