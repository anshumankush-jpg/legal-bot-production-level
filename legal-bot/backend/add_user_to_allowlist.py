"""
Script to add a user to the allowlist.
Run this to allow a user to login to the app.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.services.allowlist_service import AllowlistService

def add_user(email: str, name: str, role: str = "customer"):
    """Add a user to the allowlist."""
    db = SessionLocal()
    service = AllowlistService()
    
    try:
        user = service.create_allowlist_user(
            db=db,
            email=email,
            name=name,
            role=role
        )
        print(f"[OK] User added to allowlist!")
        print(f"    Email: {user.email}")
        print(f"    Name: {user.name}")
        print(f"    Role: {user.role}")
        print(f"    ID: {user.id}")
        print(f"\nThis user can now login at http://localhost:4200")
        return user
    except Exception as e:
        print(f"[ERROR] Failed to add user: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Default user - change these values
    EMAIL = "anshu@example.com"  # Change to your email
    NAME = "Anshu"               # Change to your name
    ROLE = "client"              # client | lawyer | employee
    
    print("=" * 60)
    print("Adding User to Allowlist")
    print("=" * 60)
    print(f"Email: {EMAIL}")
    print(f"Name: {NAME}")
    print(f"Role: {ROLE}")
    print("-" * 60)
    
    add_user(EMAIL, NAME, ROLE)
