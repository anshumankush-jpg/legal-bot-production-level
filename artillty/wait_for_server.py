"""Wait for server to be ready and check it"""
import requests
import time
import sys

max_attempts = 15
print("Waiting for server to start...")

for i in range(max_attempts):
    try:
        response = requests.get('http://localhost:8000', timeout=2)
        if response.status_code == 200:
            data = response.json()
            service = data.get('service', 'Unknown')
            print(f"\n[OK] Server is ready!")
            print(f"   Service: {service}")
            
            if "Unified Multi-Modal Embedding Server" in service:
                print("   [OK] Correct server version detected")
                sys.exit(0)
            else:
                print("   [WARNING] Different server detected")
                sys.exit(1)
    except Exception as e:
        if i < max_attempts - 1:
            print(f"   Attempt {i+1}/{max_attempts}... waiting...")
            time.sleep(2)
        else:
            print(f"\n[ERROR] Server not responding after {max_attempts} attempts")
            print(f"   Error: {e}")
            sys.exit(1)

