"""
Create Google Cloud Storage buckets for LEGID production.
Run this script to set up all required GCS buckets.

Usage:
    python setup_gcs_buckets.py --project=your-gcp-project-id
"""

import argparse
from google.cloud import storage
from google.api_core import exceptions

def create_bucket(storage_client: storage.Client, bucket_name: str, location: str = "US"):
    """Create GCS bucket if it doesn't exist."""
    try:
        bucket = storage_client.get_bucket(bucket_name)
        print(f"✅ Bucket {bucket_name} already exists")
        return bucket
    except exceptions.NotFound:
        bucket = storage_client.create_bucket(bucket_name, location=location)
        print(f"✅ Created bucket {bucket_name}")
        return bucket

def setup_bucket_cors(bucket):
    """Set CORS policy for bucket to allow frontend uploads."""
    bucket.cors = [
        {
            "origin": ["http://localhost:5173", "http://localhost:4200", "https://legid.run.app"],
            "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
            "responseHeader": ["Content-Type", "Authorization"],
            "maxAgeSeconds": 3600
        }
    ]
    bucket.patch()
    print(f"   - Set CORS policy for {bucket.name}")

def setup_bucket_lifecycle(bucket, delete_after_days: int = None):
    """Set lifecycle policy to delete old files."""
    if delete_after_days:
        bucket.lifecycle_rules = [
            {
                "action": {"type": "Delete"},
                "condition": {"age": delete_after_days}
            }
        ]
        bucket.patch()
        print(f"   - Set lifecycle policy: delete after {delete_after_days} days")

def create_folder(bucket, folder_name: str):
    """Create a 'folder' (prefix) in GCS bucket."""
    blob = bucket.blob(f"{folder_name}/.keep")
    blob.upload_from_string("")
    print(f"   - Created folder: {folder_name}/")

def main():
    parser = argparse.ArgumentParser(description="Set up GCS buckets for LEGID")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--location", default="US", help="Bucket location")
    parser.add_argument("--prefix", default="legid", help="Bucket name prefix")
    
    args = parser.parse_args()
    
    print(f"\n🚀 Creating GCS buckets for LEGID")
    print(f"   Project: {args.project}")
    print(f"   Location: {args.location}\n")
    
    # Initialize Storage client
    storage_client = storage.Client(project=args.project)
    
    # 1. Uploads bucket (user uploads: images, docs, audio)
    print("📦 Creating uploads bucket...")
    uploads_bucket_name = f"{args.prefix}-uploads-prod"
    uploads_bucket = create_bucket(storage_client, uploads_bucket_name, args.location)
    setup_bucket_cors(uploads_bucket)
    setup_bucket_lifecycle(uploads_bucket, delete_after_days=365)  # Delete after 1 year
    create_folder(uploads_bucket, "images")
    create_folder(uploads_bucket, "documents")
    create_folder(uploads_bucket, "audio")
    create_folder(uploads_bucket, "avatars")
    print()
    
    # 2. Lawyer verification bucket (sensitive documents)
    print("📦 Creating lawyer verification bucket...")
    lawyer_bucket_name = f"{args.prefix}-lawyer-verification"
    lawyer_bucket = create_bucket(storage_client, lawyer_bucket_name, args.location)
    # No CORS - these are backend-only uploads
    # No lifecycle - keep verification documents indefinitely
    create_folder(lawyer_bucket, "licenses")
    create_folder(lawyer_bucket, "id_documents")
    create_folder(lawyer_bucket, "additional_docs")
    print()
    
    # 3. Backups bucket
    print("📦 Creating backups bucket...")
    backups_bucket_name = f"{args.prefix}-backups"
    backups_bucket = create_bucket(storage_client, backups_bucket_name, args.location)
    setup_bucket_lifecycle(backups_bucket, delete_after_days=90)  # Keep backups for 90 days
    create_folder(backups_bucket, "bigquery")
    create_folder(backups_bucket, "firestore")
    print()
    
    print("✅ All buckets created successfully!\n")
    print("Bucket summary:")
    print(f"  - {uploads_bucket_name}: User uploads (1 year retention)")
    print(f"  - {lawyer_bucket_name}: Lawyer verification docs (permanent)")
    print(f"  - {backups_bucket_name}: Database backups (90 days retention)")
    print()
    print("Next steps:")
    print("1. Add these bucket names to backend/.env:")
    print(f"   GCS_UPLOADS_BUCKET={uploads_bucket_name}")
    print(f"   GCS_LAWYER_VERIFICATION_BUCKET={lawyer_bucket_name}")
    print(f"   GCS_BACKUPS_BUCKET={backups_bucket_name}")
    print()
    print("2. Grant service account permissions:")
    print(f"   gsutil iam ch serviceAccount:YOUR-SA@{args.project}.iam.gserviceaccount.com:objectAdmin gs://{uploads_bucket_name}")
    print(f"   gsutil iam ch serviceAccount:YOUR-SA@{args.project}.iam.gserviceaccount.com:objectAdmin gs://{lawyer_bucket_name}")
    print(f"   gsutil iam ch serviceAccount:YOUR-SA@{args.project}.iam.gserviceaccount.com:objectAdmin gs://{backups_bucket_name}")
    print()

if __name__ == "__main__":
    main()
