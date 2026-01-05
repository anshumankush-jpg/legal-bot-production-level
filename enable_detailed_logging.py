"""
Enable detailed logging for backend to diagnose issues
"""
import logging
import sys
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_detailed.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_backend_logs():
    """Check if backend logs exist and show recent entries"""
    log_file = Path("backend_detailed.log")
    
    if log_file.exists():
        print(f"[FOUND] Log file: {log_file}")
        print("\n[RECENT LOG ENTRIES]")
        print("="*80)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Show last 50 lines
            for line in lines[-50:]:
                print(line.rstrip())
    else:
        print("[INFO] No log file found yet - backend may not have started")

if __name__ == "__main__":
    print("="*80)
    print("BACKEND LOGGING CONFIGURATION")
    print("="*80)
    print("\n[INFO] Detailed logging enabled")
    print("[INFO] Logs will be saved to: backend_detailed.log")
    print("[INFO] Logs will also appear in console")
    print("\n[NOTE] Restart backend to apply logging configuration")
    print("="*80)
    
    check_backend_logs()
