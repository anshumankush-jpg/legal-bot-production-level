"""
Run all tests with detailed logging
"""
import subprocess
import sys
import time
from datetime import datetime

def run_tests():
    """Run all test suites"""
    print("="*80)
    print("RUNNING ALL TESTS WITH DETAILED LOGGING")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Backend tests
    print("="*80)
    print("PHASE 1: BACKEND TESTS")
    print("="*80)
    try:
        result = subprocess.run(
            [sys.executable, "test_backend_comprehensive.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.TimeoutExpired:
        print("[ERROR] Backend tests timed out")
    except Exception as e:
        print(f"[ERROR] Backend tests failed: {e}")
    
    print("\n")
    time.sleep(2)
    
    # Test 2: Frontend/Backend integration tests
    print("="*80)
    print("PHASE 2: FRONTEND/BACKEND INTEGRATION TESTS")
    print("="*80)
    try:
        result = subprocess.run(
            [sys.executable, "test_frontend_comprehensive.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.TimeoutExpired:
        print("[ERROR] Frontend tests timed out")
    except Exception as e:
        print(f"[ERROR] Frontend tests failed: {e}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    print("\n[LOG FILES]")
    print("  - backend_detailed.log (backend logs)")
    print("  - backend_test_results.json (backend test results)")
    print("  - frontend_test_results.json (frontend test results)")
    print("\n[CHECK LOGS] to identify problems!")

if __name__ == "__main__":
    run_tests()
