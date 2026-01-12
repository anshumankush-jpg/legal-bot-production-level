"""
Script to add multiple users to the allowlist.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.services.allowlist_service import AllowlistService

def add_users():
    """Add multiple test users to allowlist."""
    db = SessionLocal()
    service = AllowlistService()
    
    # List of users to add
    users_to_add = [
        {"email": "anshu@example.com", "name": "Anshu", "role": "client"},
        {"email": "test@example.com", "name": "Test User", "role": "client"},
        {"email": "lawyer@example.com", "name": "Test Lawyer", "role": "lawyer"},
        {"email": "admin@example.com", "name": "Admin User", "role": "employee_admin"},
    ]
    
    print("=" * 60)
    print("Adding Multiple Users to Allowlist")
    print("=" * 60)
    
    added_count = 0
    for user_data in users_to_add:
        try:
            user = service.create_allowlist_user(
                db=db,
                email=user_data['email'],
                name=user_data['name'],
                role=user_data['role']
            )
            print(f"[OK] {user_data['email']} - {user_data['name']} ({user_data['role']})")
            added_count += 1
        except Exception as e:
            print(f"[SKIP] {user_data['email']} - {str(e)}")
    
    db.close()
    
    print("-" * 60)
    print(f"[DONE] Added/verified {added_count} users")
    print("\nThese users can now login at http://localhost:4200")
    print("\nTo add your own Gmail:")
    print("  Edit this script and add your email to users_to_add list")

if __name__ == "__main__":
    add_users()
