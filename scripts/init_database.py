#!/usr/bin/env python3
"""
Initialize Demo Copilot Database
Creates tables and seeds initial data
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.connection import engine, init_db, check_db_connection
from database.models import Base, DemoScript
from sqlalchemy.orm import Session
import uuid


def seed_demo_scripts(session: Session):
    """Seed initial demo scripts"""
    print("Seeding demo scripts...")

    # InSign Standard Demo Script
    insign_script = DemoScript(
        id="insign-standard-v1",
        product_name="insign",
        script_version="1.0",
        script_type="standard",
        steps=[
            {"step": 1, "name": "login", "description": "Login to InSign platform", "duration_seconds": 30},
            {"step": 2, "name": "dashboard", "description": "Overview of dashboard features", "duration_seconds": 90},
            {"step": 3, "name": "sign_document", "description": "Sign a document demo", "duration_seconds": 180},
            {"step": 4, "name": "send_document", "description": "Send document for signature", "duration_seconds": 120},
            {"step": 5, "name": "audit_trail", "description": "Review audit trail and compliance", "duration_seconds": 90}
        ],
        total_duration_estimate_minutes=10,
        product_description="InSign is a modern electronic signature platform that simplifies document signing and management. It's a powerful alternative to DocuSign with better pricing and user experience.",
        key_features=[
            "Unlimited document signing",
            "Template library with smart field detection",
            "Bulk send capabilities",
            "Real-time notifications and reminders",
            "Comprehensive audit trails for compliance",
            "Mobile apps for iOS and Android",
            "Integrations with Salesforce, Google Drive, Dropbox",
            "Advanced authentication (SSO, 2FA)",
            "Custom branding and white-labeling",
            "API access for custom integrations"
        ],
        pricing_info="Starting at $10/user/month for Pro plan, with Enterprise options available. 50% more affordable than DocuSign.",
        target_customers=[
            "SMBs needing 5-100 users",
            "Sales teams sending contracts",
            "HR departments for onboarding",
            "Real estate agencies",
            "Legal firms",
            "Financial services"
        ],
        is_active=True
    )

    # Check if exists
    existing = session.query(DemoScript).filter(
        DemoScript.id == insign_script.id
    ).first()

    if not existing:
        session.add(insign_script)
        print("✓ Added InSign standard demo script")
    else:
        print("- InSign standard demo script already exists")

    # InSign Quick Demo Script
    insign_quick = DemoScript(
        id="insign-quick-v1",
        product_name="insign",
        script_version="1.0",
        script_type="quick",
        steps=[
            {"step": 1, "name": "login", "description": "Quick login", "duration_seconds": 15},
            {"step": 2, "name": "sign_document", "description": "Quick sign demo", "duration_seconds": 90},
            {"step": 3, "name": "send_document", "description": "Quick send demo", "duration_seconds": 60}
        ],
        total_duration_estimate_minutes=5,
        product_description="InSign is a modern electronic signature platform that simplifies document signing and management.",
        key_features=insign_script.key_features,
        pricing_info=insign_script.pricing_info,
        target_customers=insign_script.target_customers,
        is_active=True
    )

    existing_quick = session.query(DemoScript).filter(
        DemoScript.id == insign_quick.id
    ).first()

    if not existing_quick:
        session.add(insign_quick)
        print("✓ Added InSign quick demo script")
    else:
        print("- InSign quick demo script already exists")

    session.commit()
    print("✓ Demo scripts seeded successfully")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Demo Copilot Database Initialization")
    print("=" * 60)

    # Check connection
    print("\n1. Checking database connection...")
    if not check_db_connection():
        print("✗ Database connection failed!")
        print("  Please check your DATABASE_URL in .env")
        sys.exit(1)
    print("✓ Database connection successful")

    # Create tables
    print("\n2. Creating database tables...")
    try:
        init_db()
        print("✓ Database tables created")
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        sys.exit(1)

    # Seed data
    print("\n3. Seeding initial data...")
    try:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        seed_demo_scripts(session)

        session.close()
        print("✓ Initial data seeded")
    except Exception as e:
        print(f"✗ Failed to seed data: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ Database initialization complete!")
    print("=" * 60)
    print("\nYou can now start the API server:")
    print("  cd backend")
    print("  python -m api.main")
    print()


if __name__ == "__main__":
    main()
