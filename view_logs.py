"""
View and analyze backend logs to identify problems
"""
import os
from pathlib import Path
from datetime import datetime

def view_backend_logs():
    """View backend log file"""
    log_file = Path("backend_detailed.log")
    
    print("="*80)
    print("BACKEND LOG VIEWER")
    print("="*80)
    
    if not log_file.exists():
        print("[INFO] No log file found: backend_detailed.log")
        print("[TIP] Start backend to generate logs")
        return
    
    print(f"[FOUND] Log file: {log_file}")
    print(f"[SIZE] {log_file.stat().st_size} bytes")
    print("\n[RECENT LOG ENTRIES - Last 100 lines]")
    print("="*80)
    
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        for line in lines[-100:]:
            print(line.rstrip())
    
    # Analyze errors
    print("\n" + "="*80)
    print("ERROR ANALYSIS")
    print("="*80)
    
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        errors = [line for line in content.split('\n') if 'ERROR' in line.upper() or 'EXCEPTION' in line.upper()]
        
        if errors:
            print(f"[FOUND] {len(errors)} error entries")
            print("\n[RECENT ERRORS]")
            for error in errors[-10:]:
                print(f"  {error}")
        else:
            print("[OK] No errors found in logs")

def view_test_results():
    """View test results"""
    import json
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    # Backend test results
    backend_results = Path("backend_test_results.json")
    if backend_results.exists():
        print("\n[BACKEND TEST RESULTS]")
        with open(backend_results, 'r') as f:
            data = json.load(f)
            summary = data.get('summary', {})
            print(f"  Total: {summary.get('total', 0)}")
            print(f"  Passed: {summary.get('passed', 0)}")
            print(f"  Failed: {summary.get('failed', 0)}")
            
            # Show failed tests
            failed = [t for t in data.get('tests', []) if t.get('status') == 'FAIL']
            if failed:
                print(f"\n  [FAILED TESTS]")
                for test in failed:
                    print(f"    - {test.get('test')}: {test.get('details', '')}")
    
    # Frontend test results
    frontend_results = Path("frontend_test_results.json")
    if frontend_results.exists():
        print("\n[FRONTEND TEST RESULTS]")
        with open(frontend_results, 'r') as f:
            data = json.load(f)
            summary = data.get('summary', {})
            print(f"  Total: {summary.get('total', 0)}")
            print(f"  Passed: {summary.get('passed', 0)}")
            print(f"  Failed: {summary.get('failed', 0)}")
            
            # Show failed tests
            failed = [t for t in data.get('tests', []) if t.get('status') == 'FAIL']
            if failed:
                print(f"\n  [FAILED TESTS]")
                for test in failed:
                    print(f"    - {test.get('test')}: {test.get('details', '')}")

if __name__ == "__main__":
    view_backend_logs()
    view_test_results()
    print("\n" + "="*80)
    print("[TIP] Check the logs above to identify the main problem!")
    print("="*80)
