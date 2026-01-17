"""
Create BigQuery tables for LEGID production database.
Run this script to set up all required tables.

Usage:
    python create_tables.py --project=your-gcp-project-id --dataset=legid_production
"""

import os
import argparse
from google.cloud import bigquery
from google.api_core import exceptions

def create_dataset(client: bigquery.Client, dataset_id: str, location: str = "US"):
    """Create BigQuery dataset if it doesn't exist."""
    dataset_ref = client.dataset(dataset_id)
    
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset {dataset_id} already exists")
    except exceptions.NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        dataset.description = "LEGID Legal AI Production Database"
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"✅ Created dataset {dataset_id}")

def create_users_table(client: bigquery.Client, table_id: str):
    """Create users table."""
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("password_hash", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("display_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("username", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("avatar_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("auth_provider", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("google_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("email_verified", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("last_login", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "User accounts with authentication details"
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id}")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_user_preferences_table(client: bigquery.Client, table_id: str):
    """Create user_preferences table."""
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("theme", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("font_size", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("response_style", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("language", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("auto_read", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("cookies_accepted", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("notification_email", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("notification_push", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "User personalization preferences"
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id}")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_conversations_table(client: bigquery.Client, table_id: str):
    """Create conversations table."""
    schema = [
        bigquery.SchemaField("conversation_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("law_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("law_category", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("jurisdiction", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("message_count", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "Chat conversations - each New Chat creates a new conversation"
    table.clustering_fields = ["user_id", "created_at"]
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id} with clustering")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_messages_table(client: bigquery.Client, table_id: str):
    """Create messages table."""
    schema = [
        bigquery.SchemaField("message_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("conversation_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("citations", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("edited_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("deleted", "BOOL", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "Individual messages within conversations"
    table.clustering_fields = ["conversation_id", "created_at"]
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id} with clustering")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_uploads_table(client: bigquery.Client, table_id: str):
    """Create uploads table."""
    schema = [
        bigquery.SchemaField("upload_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("conversation_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("filename", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("file_size", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("mime_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("gcs_url", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("gcs_bucket", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("gcs_path", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("ocr_text", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("chunks_indexed", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("processing_status", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "User-uploaded files stored in GCS"
    table.clustering_fields = ["user_id", "created_at"]
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id} with clustering")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_lawyer_verification_table(client: bigquery.Client, table_id: str):
    """Create lawyer_verification table."""
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("bar_country", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("bar_province_state", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("bar_number", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("license_upload_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("id_upload_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("additional_docs_upload_ids", "STRING", mode="REPEATED"),
        bigquery.SchemaField("reviewer_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("review_notes", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("submitted_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("reviewed_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("approved_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "Lawyer verification applications and status"
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id}")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_sessions_table(client: bigquery.Client, table_id: str):
    """Create sessions table."""
    schema = [
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("token_hash", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("device_info", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("ip_address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("expires_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("last_active", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("is_active", "BOOL", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "User sessions for JWT token tracking"
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id}")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_audit_log_table(client: bigquery.Client, table_id: str):
    """Create audit_log table."""
    schema = [
        bigquery.SchemaField("log_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("action", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("resource_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("resource_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("details", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("ip_address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "Audit trail for all user actions"
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id}")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_cookie_consent_table(client: bigquery.Client, table_id: str):
    """Create cookie_consent table."""
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("consent_given", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("necessary_cookies", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("analytics_cookies", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("marketing_cookies", "BOOL", mode="NULLABLE"),
        bigquery.SchemaField("consent_date", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("ip_address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "Cookie consent tracking for GDPR compliance"
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id}")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def create_analytics_table(client: bigquery.Client, table_id: str):
    """Create analytics table."""
    schema = [
        bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("event_data", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("session_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.description = "Analytics events for usage tracking"
    
    try:
        table = client.create_table(table)
        print(f"✅ Created table {table.table_id}")
    except exceptions.Conflict:
        print(f"⚠️  Table {table_id.split('.')[-1]} already exists")

def main():
    parser = argparse.ArgumentParser(description="Create BigQuery tables for LEGID")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--dataset", default="legid_production", help="BigQuery dataset name")
    parser.add_argument("--location", default="US", help="BigQuery dataset location")
    
    args = parser.parse_args()
    
    print(f"\n🚀 Creating BigQuery tables for LEGID")
    print(f"   Project: {args.project}")
    print(f"   Dataset: {args.dataset}")
    print(f"   Location: {args.location}\n")
    
    # Initialize BigQuery client
    client = bigquery.Client(project=args.project)
    
    # Create dataset
    create_dataset(client, args.dataset, args.location)
    
    # Create all tables
    dataset_id = f"{args.project}.{args.dataset}"
    
    print("\n📊 Creating tables...\n")
    
    create_users_table(client, f"{dataset_id}.users")
    create_user_preferences_table(client, f"{dataset_id}.user_preferences")
    create_conversations_table(client, f"{dataset_id}.conversations")
    create_messages_table(client, f"{dataset_id}.messages")
    create_uploads_table(client, f"{dataset_id}.uploads")
    create_lawyer_verification_table(client, f"{dataset_id}.lawyer_verification")
    create_sessions_table(client, f"{dataset_id}.sessions")
    create_audit_log_table(client, f"{dataset_id}.audit_log")
    create_cookie_consent_table(client, f"{dataset_id}.cookie_consent")
    create_analytics_table(client, f"{dataset_id}.analytics")
    
    print("\n✅ All tables created successfully!\n")
    print("Next steps:")
    print("1. Set up GCS buckets: python scripts/setup_gcs_buckets.py")
    print("2. Configure backend/.env with BigQuery credentials")
    print("3. Start backend: cd backend && uvicorn app.main:app --reload")
    print("4. Start frontend: cd frontend && npm run dev\n")

if __name__ == "__main__":
    main()
