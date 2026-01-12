"""
Final script to update .env with correct Google OAuth credentials.
"""
from pathlib import Path

def update_env():
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("[ERROR] .env file not found!")
        return
    
    # Read existing content
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace Client ID and Secret
    content = content.replace(
        'GOOGLE_CLIENT_ID=1086283983680-m0rg0loe9ktg0vd4rv5onmarr8lgpqbu.apps.googleusercontent.com',
        'GOOGLE_CLIENT_ID=1086283983680-cnmfcbrv2d8hhc047llkog1nkhbu01tm.apps.googleusercontent.com'
    )
    
    content = content.replace(
        'GOOGLE_CLIENT_SECRET=REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE',
        'GOOGLE_CLIENT_SECRET=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'
    )
    
    # Write back
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("[OK] .env file updated with Google OAuth credentials!")
    print("\nConfigured:")
    print("  Client ID:     1086283983680-cnmfcbrv2d8hhc047llkog1nkhbu01tm.apps.googleusercontent.com")
    print("  Client Secret: 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")
    print("  Redirect URI:  http://localhost:5173/auth/callback/google")
    print("\n[OK] Ready to test!")

if __name__ == "__main__":
    update_env()
