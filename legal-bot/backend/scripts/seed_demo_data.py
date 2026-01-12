"""
Seed script for creating demo data for testing.

This script creates:
- Demo users for each role (client, lawyer, employee, employee_admin)
- Sample matters
- Employee assignments
- Sample messages and documents

Run: python -m scripts.seed_demo_data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models.db_models import (
    User, UserRole, MatterDB, Message, Document,
    EmployeeAssignment, LawyerProfile
)
from app.services.auth_service import AuthService
from datetime import datetime, timedelta
import uuid


def seed_users(db):
    """Create demo users for each role."""
    print("Creating demo users...")
    
    users = []
    
    # Client user
    client = User(
        email="client@demo.com",
        password_hash=AuthService.hash_password("password123"),
        name="John Client",
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=True
    )
    db.add(client)
    users.append(("client", client))
    
    # Lawyer user
    lawyer = User(
        email="lawyer@demo.com",
        password_hash=AuthService.hash_password("password123"),
        name="Jane Lawyer",
        role=UserRole.LAWYER,
        is_active=True,
        is_verified=True
    )
    db.add(lawyer)
    users.append(("lawyer", lawyer))
    
    # Employee user
    employee = User(
        email="employee@demo.com",
        password_hash=AuthService.hash_password("password123"),
        name="Bob Employee",
        role=UserRole.EMPLOYEE,
        is_active=True,
        is_verified=True
    )
    db.add(employee)
    users.append(("employee", employee))
    
    # Employee admin user
    admin = User(
        email="admin@demo.com",
        password_hash=AuthService.hash_password("password123"),
        name="Alice Admin",
        role=UserRole.EMPLOYEE_ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    users.append(("admin", admin))
    
    # Commit users first to get IDs
    db.commit()
    
    # Now create lawyer profile (after commit, so lawyer.id exists)
    lawyer_profile = LawyerProfile(
        user_id=lawyer.id,
        bar_number="BAR123456",
        firm_name="Demo Law Firm",
        specializations=["Family Law", "Criminal Law"],
        years_experience=10,
        bio="Experienced lawyer specializing in family and criminal law.",
        consultation_fee=15000,  # $150 in cents
        accepts_new_clients=True
    )
    db.add(lawyer_profile)
    db.commit()
    
    print(f"[OK] Created {len(users)} demo users")
    return dict(users)


def seed_matters(db, users):
    """Create sample matters."""
    print("Creating sample matters...")
    
    client = users["client"]
    
    matters = []
    
    # Matter 1: Traffic ticket
    matter1 = MatterDB(
        user_id=client.id,
        title="Traffic Ticket - Speeding Violation",
        description="Received a speeding ticket on Highway 101. Need help understanding options.",
        matter_type="traffic_ticket",
        status="active",
        jurisdiction_data={
            "country": "US",
            "region": "California",
            "region_code": "CA"
        },
        structured_data={
            "ticket_number": "CA-2024-12345",
            "violation": "Speeding",
            "speed": "75 mph in 55 mph zone"
        }
    )
    db.add(matter1)
    matters.append(matter1)
    
    # Matter 2: Contract dispute
    matter2 = MatterDB(
        user_id=client.id,
        title="Contract Dispute with Contractor",
        description="Contractor did not complete work as agreed. Need legal advice.",
        matter_type="contract",
        status="active",
        jurisdiction_data={
            "country": "US",
            "region": "California",
            "region_code": "CA"
        },
        structured_data={
            "contract_date": "2024-01-15",
            "amount": "$5,000"
        }
    )
    db.add(matter2)
    matters.append(matter2)
    
    # Matter 3: Closed matter
    matter3 = MatterDB(
        user_id=client.id,
        title="Lease Agreement Review",
        description="Needed help reviewing apartment lease. Completed.",
        matter_type="lease",
        status="closed",
        jurisdiction_data={
            "country": "US",
            "region": "California",
            "region_code": "CA"
        },
        closed_at=datetime.utcnow() - timedelta(days=7)
    )
    db.add(matter3)
    matters.append(matter3)
    
    db.commit()
    
    print(f"[OK] Created {len(matters)} sample matters")
    return matters


def seed_messages(db, matters):
    """Create sample messages for matters."""
    print("Creating sample messages...")
    
    count = 0
    
    for matter in matters[:2]:  # Only for active matters
        # User message
        msg1 = Message(
            matter_id=matter.id,
            role="user",
            content=f"I need help with {matter.title}. What are my options?",
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        db.add(msg1)
        count += 1
        
        # Assistant response
        msg2 = Message(
            matter_id=matter.id,
            role="assistant",
            content="I understand you need legal information. Let me help you understand your options. Based on your situation, here are some key points to consider...",
            created_at=datetime.utcnow() - timedelta(hours=2, minutes=-5)
        )
        db.add(msg2)
        count += 1
        
        # Follow-up
        msg3 = Message(
            matter_id=matter.id,
            role="user",
            content="Thank you, that's helpful. What should I do next?",
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        db.add(msg3)
        count += 1
    
    db.commit()
    
    print(f"[OK] Created {count} sample messages")


def seed_documents(db, matters):
    """Create sample document records."""
    print("Creating sample documents...")
    
    count = 0
    
    for matter in matters[:2]:
        # Uploaded document
        doc1 = Document(
            matter_id=matter.id,
            filename="evidence_document.pdf",
            file_type="application/pdf",
            file_size=245678,
            storage_path=f"data/uploads/{matter.id}/evidence_document.pdf",
            document_type="uploaded",
            meta_data={"uploaded_by": "user"}
        )
        db.add(doc1)
        count += 1
        
        # Generated document
        doc2 = Document(
            matter_id=matter.id,
            filename="legal_summary.pdf",
            file_type="application/pdf",
            file_size=123456,
            storage_path=f"data/uploads/{matter.id}/legal_summary.pdf",
            document_type="generated",
            meta_data={"generated_by": "system"}
        )
        db.add(doc2)
        count += 1
    
    db.commit()
    
    print(f"[OK] Created {count} sample documents")


def seed_employee_assignments(db, users, matters):
    """Create employee assignments to matters."""
    print("Creating employee assignments...")
    
    employee = users["employee"]
    admin = users["admin"]
    
    # Assign employee to first matter
    assignment1 = EmployeeAssignment(
        employee_user_id=employee.id,
        matter_id=matters[0].id,
        assigned_by_user_id=admin.id
    )
    db.add(assignment1)
    
    # Assign employee to second matter
    assignment2 = EmployeeAssignment(
        employee_user_id=employee.id,
        matter_id=matters[1].id,
        assigned_by_user_id=admin.id
    )
    db.add(assignment2)
    
    db.commit()
    
    print("[OK] Created 2 employee assignments")


def main():
    """Main seed function."""
    print("\n" + "="*60)
    print("LEGID Demo Data Seeder")
    print("="*60 + "\n")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print("[OK] Database initialized\n")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).filter(User.email.like("%@demo.com")).count()
        if existing_users > 0:
            print(f"[WARNING] Found {existing_users} existing demo users")
            response = input("Do you want to continue? This may create duplicates. (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        # Seed data
        users = seed_users(db)
        matters = seed_matters(db, users)
        seed_messages(db, matters)
        seed_documents(db, matters)
        seed_employee_assignments(db, users, matters)
        
        print("\n" + "="*60)
        print("[OK] Demo data seeded successfully!")
        print("="*60 + "\n")
        
        print("Demo Users Created:")
        print("-" * 60)
        print(f"Client:         email: client@demo.com     password: password123")
        print(f"Lawyer:         email: lawyer@demo.com     password: password123")
        print(f"Employee:       email: employee@demo.com   password: password123")
        print(f"Employee Admin: email: admin@demo.com      password: password123")
        print("-" * 60)
        
        print("\nYou can now:")
        print("1. Start the backend: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Login with any of the demo accounts above")
        print("\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
