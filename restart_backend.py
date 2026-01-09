#!/usr/bin/env python3
"""Script to restart the backend server and check for proxy-related errors."""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 60)
print("Checking for proxy-related configuration issues...")
print("=" * 60)

# Check environment variables
print("\n1. Checking environment variables:")
env_vars = ['OPENAI_PROXIES', 'PROXIES', 'HTTP_PROXY', 'HTTPS_PROXY']
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"   WARNING: {var} = {value}")
    else:
        print(f"   OK: {var} = (not set)")

# Check settings
print("\n2. Checking settings for proxy-related attributes:")
try:
    from app.core.config import settings
    proxy_attrs = [a for a in dir(settings) if 'proxy' in a.lower() and not a.startswith('_')]
    if proxy_attrs:
        print(f"   WARNING: Found proxy attributes: {proxy_attrs}")
        for attr in proxy_attrs:
            print(f"      - {attr} = {getattr(settings, attr, 'N/A')}")
    else:
        print("   OK: No proxy-related attributes found in settings")
except Exception as e:
    print(f"   ERROR: Error checking settings: {e}")

# Reset client cache
print("\n3. Resetting OpenAI client cache...")
try:
    from app.core.openai_client_unified import reset_openai_clients
    reset_openai_clients()
    print("   OK: Client cache reset successfully")
except Exception as e:
    print(f"   ERROR: Error resetting cache: {e}")

# Test client creation
print("\n4. Testing OpenAI client creation...")
try:
    from app.core.openai_client_unified import get_openai_client
    from app.core.config import settings
    
    if not settings.OPENAI_API_KEY:
        print("   WARNING: OPENAI_API_KEY not set - skipping client test")
    else:
        client = get_openai_client()
        print("   OK: OpenAI client created successfully")
        print(f"   OK: Client type: {type(client)}")
except Exception as e:
    print(f"   ERROR: Error creating client: {e}")
    import traceback
    print(f"\n   Full traceback:\n{traceback.format_exc()}")

print("\n" + "=" * 60)
print("Backend check complete!")
print("=" * 60)
print("\nTo start the server, run:")
print("  python start_server.py")
print("  or")
print("  cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
