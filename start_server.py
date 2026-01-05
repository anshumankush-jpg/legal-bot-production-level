#!/usr/bin/env python3
"""Simple server startup script for PLAZA-AI Artillery"""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("[START] Starting PLAZA-AI Artillery Server...")
    print("[INFO] Backend URL: http://localhost:8000")
    print("[INFO] Frontend URL: http://localhost:3000")
    print("[INFO] Test API: python test_local_api.py")
    print("=" * 50)

    try:
        from backend.app.main import app
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)