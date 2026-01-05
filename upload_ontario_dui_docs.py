"""
Upload Ontario DUI-related legal documents to the Artillery backend
"""
import requests
import os
from pathlib import Path
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BACKEND_URL = "http://127.0.0.1:8000"

def upload_document(file_path, user_id="default_user", offence_number=None):
    """Upload a document to the backend"""
    url = f"{BACKEND_URL}/api/artillery/upload"
    
    file_name = os.path.basename(file_path)
    print(f"\nUploading: {file_name}")
    print(f"   Path: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            data = {
                'user_id': user_id,
            }
            if offence_number:
                data['offence_number'] = offence_number
            
            response = requests.post(url, files=files, data=data, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS: {result.get('message', 'Uploaded')}")
                print(f"   Chunks: {result.get('chunks_created', 0)}")
                return True
            else:
                print(f"   FAILED: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

def main():
    print("="*80)
    print("UPLOADING ONTARIO DUI LEGAL DOCUMENTS TO BACKEND")
    print("="*80)
    
    # Documents to upload for Ontario DUI questions
    documents = [
        {
            'path': 'CANADA TRAFFIC FILES/ontario_highway_traffic_act.html',
            'offence': 'DUI-ONTARIO',
            'description': 'Ontario Highway Traffic Act (contains DUI penalties)'
        },
        {
            'path': 'canada criminal and federal law/canada_criminal_code_c46.pdf',
            'offence': 'DUI-CRIMINAL',
            'description': 'Canada Criminal Code (DUI criminal charges)'
        },
        {
            'path': 'paralegal_advice_dataset/canada/CAN-ON-TRAFFIC-0001.json',
            'offence': 'DUI-ONTARIO-CASE',
            'description': 'Ontario traffic case examples'
        },
        {
            'path': 'canada criminal and federal law/ontario_provincial_offences_act_90p33.html',
            'offence': 'DUI-ONTARIO-POA',
            'description': 'Ontario Provincial Offences Act'
        }
    ]
    
    uploaded = 0
    failed = 0
    
    for doc in documents:
        file_path = doc['path']
        if os.path.exists(file_path):
            print(f"\n{doc['description']}")
            if upload_document(file_path, offence_number=doc['offence']):
                uploaded += 1
            else:
                failed += 1
        else:
            print(f"\nSKIPPED: {doc['description']}")
            print(f"   File not found: {file_path}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"UPLOAD SUMMARY")
    print("="*80)
    print(f"Successfully uploaded: {uploaded}")
    print(f"Failed/Skipped: {failed}")
    print(f"Total attempted: {len(documents)}")
    
    if uploaded > 0:
        print("\nDocuments are now being processed!")
        print("Wait 10-20 seconds for embedding to complete...")
        print("Then ask: 'What are DUI penalties in Ontario?'")
    
    return uploaded > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\nReady to test the bot!")
    else:
        print("\nNo documents were uploaded. Check the paths and try again.")
