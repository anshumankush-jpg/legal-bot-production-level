"""Update .env with correct Google OAuth credentials from JSON."""
from pathlib import Path

env_path = Path(__file__).parent / ".env"

if not env_path.exists():
    print("[ERROR] .env not found")
    exit(1)

# Read content
with open(env_path, 'r') as f:
    content = f.read()

# Update with correct credentials
old_client_id = "1086283983680-m0rg0loe9ktg0vd4rv5onmarr8lgpqbu.apps.googleusercontent.com"
new_client_id = "1086283983680-cnmfcbrv2d8hhc047llkog1nkhbu01tm.apps.googleusercontent.com"

old_secret = "REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE"
new_secret = "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"

content = content.replace(old_client_id, new_client_id)
content = content.replace(old_secret, new_secret)

# Write back
with open(env_path, 'w') as f:
    f.write(content)

print("[OK] Updated .env with correct Google OAuth credentials!")
print("\nClient ID: 1086283983680-cnmfcbrv2d8hhc047llkog1nkhbu01tm...")
print("Client Secret: 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")
