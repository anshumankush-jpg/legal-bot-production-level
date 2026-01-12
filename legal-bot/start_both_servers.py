#!/usr/bin/env python3
"""
PLAZA-AI - Start Both Backend and Frontend Servers
Cross-platform Python script to start both servers
"""
import subprocess
import sys
import time
import os
import platform
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}[SUCCESS] {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARNING] {text}{Colors.RESET}")

def check_dependencies():
    """Check if required dependencies are available"""
    print_info("Checking dependencies...")
    
    # Check Python
    try:
        python_version = sys.version_info
        print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except:
        print_error("Python not found!")
        return False
    
    # Check if backend directory exists
    if not Path("backend/app/main.py").exists():
        print_error("Backend directory not found!")
        print_info("Please run this script from the PLAZA-AI root directory.")
        return False
    
    # Check if frontend directory exists
    if not Path("frontend/package.json").exists():
        print_error("Frontend directory not found!")
        print_info("Please run this script from the PLAZA-AI root directory.")
        return False
    
    # Check if npm is available
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"npm {result.stdout.strip()}")
        else:
            print_warning("npm not found - frontend may not start")
    except:
        print_warning("npm not found - frontend may not start")
    
    return True

def start_backend():
    """Start the backend server"""
    print_info("Starting Backend Server...")
    print_info("Backend will run on: http://localhost:8000")
    
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload"
    ]
    
    try:
        if platform.system() == "Windows":
            # On Windows, start in a new console window
            subprocess.Popen(
                backend_cmd,
                cwd="backend",
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix-like systems, start in background
            subprocess.Popen(
                backend_cmd,
                cwd="backend",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print_success("Backend server started!")
        return True
    except Exception as e:
        print_error(f"Failed to start backend: {str(e)}")
        return False

def start_frontend():
    """Start the frontend server"""
    print_info("Starting Frontend Server...")
    print_info("Frontend will run on: http://localhost:4200")
    
    frontend_cmd = ["npm", "start"]
    
    try:
        if platform.system() == "Windows":
            # On Windows, start in a new console window
            subprocess.Popen(
                frontend_cmd,
                cwd="frontend",
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix-like systems, start in background
            subprocess.Popen(
                frontend_cmd,
                cwd="frontend",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print_success("Frontend server started!")
        return True
    except Exception as e:
        print_error(f"Failed to start frontend: {str(e)}")
        return False

def wait_for_backend(max_wait=30):
    """Wait for backend to be ready"""
    import requests
    
    print_info("Waiting for backend to be ready...")
    
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print_success("Backend is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
        if i % 5 == 0:
            print_info(f"Still waiting... ({i}/{max_wait} seconds)")
    
    print_warning("Backend may not be ready yet, but continuing...")
    return False

def main():
    """Main function"""
    print_header("PLAZA-AI - Starting Backend and Frontend Servers")
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print_error("Please run this script from the PLAZA-AI root directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    
    # Start backend
    if not start_backend():
        print_error("Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend
    if not start_frontend():
        print_warning("Failed to start frontend. Backend is still running.")
    
    # Wait for backend to be ready
    wait_for_backend()
    
    print()
    print_header("Servers Started Successfully!")
    print()
    print_success("Backend:  http://localhost:8000")
    print_success("Frontend: http://localhost:4200")
    print()
    print_info("Both servers are running in separate windows/processes.")
    print_info("The frontend should automatically open in your browser.")
    print()
    print_warning("To stop the servers, close the respective windows or use Ctrl+C.")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Script interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
