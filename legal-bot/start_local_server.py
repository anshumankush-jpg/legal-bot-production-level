#!/usr/bin/env python3
"""Simple script to start the PLAZA-AI backend server locally"""

import uvicorn
import sys
from pathlib import Path

def main():
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    print("Starting PLAZA-AI Backend Server...")
    print("Server will be available at: http://localhost:8000")
    print("Artillery endpoints: /api/artillery/*")
    print("Health check: http://localhost:8000/api/artillery/health")
    print("\nPress Ctrl+C to stop the server\n")

    try:
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())