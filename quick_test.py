import requests

try:
    response = requests.get('http://localhost:8000/api/artillery/health', timeout=5)
    print(f'Health check: HTTP {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Status: {data.get("status")}')
        print(f'Index size: {data.get("faiss_index_size")}')
        print(f'Models loaded: {data.get("models_loaded")}')
    else:
        print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}')