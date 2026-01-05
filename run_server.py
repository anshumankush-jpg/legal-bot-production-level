#!/usr/bin/env python3
"""Server startup script for PLAZA-AI Artillery"""

import uvicorn
import sys
from pathlib import Path

# Add paths - project root first, then backend
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))  # Backend first for backend.app.main
sys.path.insert(0, str(project_root))  # Project root for artillery modules

if __name__ == "__main__":
    print("[START] Starting PLAZA-AI Artillery Server...")
    print("[INFO] Backend URL: http://localhost:8000")
    print("[INFO] Frontend URL: http://localhost:3000")
    print("[INFO] Test API: python test_local_api.py")
    print("=" * 50)

    try:
        from backend.app.main import app
        print("[SUCCESS] App loaded successfully")
        uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)