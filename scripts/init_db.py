"""
Database initialization script.

Creates all tables and seeds initial data (4 businesses, 8 team members).
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.infrastructure.database.models import Base, BusinessORM, MemberORM


def init_database():
    """Initialize database with tables and seed data."""
    print("[*] Initializing database...")

    # Create sync engine
    sync_db_url = settings.database_url.replace('+asyncpg', '')
    engine = create_engine(sync_db_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)

    # Create all tables
    with engine.begin() as conn:
        print("[*] Enabling pgvector extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        print("[*] Creating tables...")
        Base.metadata.create_all(bind=engine)

    print("[OK] Tables created successfully!")

    # Seed initial data
    with SessionLocal() as session:
        # Check if businesses already exist
        result = session.execute(select(BusinessORM))
        existing_businesses = result.scalars().all()

        if not existing_businesses:
            print("[*] Seeding businesses...")
            businesses = [
                BusinessORM(
                    id=1,
                    name="Inventum",
                    description="Ремонт стоматологического оборудования"
                ),
                BusinessORM(
                    id=2,
                    name="Inventum Lab",
                    description="Зуботехническая лаборатория"
                ),
                BusinessORM(
                    id=3,
                    name="R&D",
                    description="Разработка прототипов"
                ),
                BusinessORM(
                    id=4,
                    name="Import & Trade",
                    description="Импорт оборудования из Китая"
                ),
            ]
            session.add_all(businesses)
            print("[OK] 4 businesses added")
        else:
            print("[INFO] Businesses already exist, skipping...")

        # Check if members already exist
        result = session.execute(select(MemberORM))
        existing_members = result.scalars().all()

        if not existing_members:
            print("[*] Seeding team members...")
            members = [
                # Leadership
                MemberORM(name="Константин", role="CEO", business_ids=[1, 2, 3, 4]),
                MemberORM(name="Лиза", role="Маркетинг/SMM", business_ids=[1, 2, 3, 4]),

                # Inventum
                MemberORM(name="Максим", role="Директор", business_ids=[1, 3]),
                MemberORM(name="Дима", role="Мастер", business_ids=[1, 3]),
                MemberORM(name="Максут", role="Выездной мастер", business_ids=[1]),

                # Inventum Lab
                MemberORM(name="Юрий Владимирович", role="Директор", business_ids=[2]),
                MemberORM(name="Мария", role="CAD/CAM оператор", business_ids=[2]),

                # Import & Trade
                MemberORM(name="Слава", role="Юрист/бухгалтер", business_ids=[4]),
            ]
            session.add_all(members)
            print("[OK] 8 team members added")
        else:
            print("[INFO] Team members already exist, skipping...")

        session.commit()

    print("[SUCCESS] Database initialization complete!")
    print("\n[SUMMARY]")
    print("  - Tables: created")
    print("  - pgvector: enabled")
    print("  - Businesses: 4")
    print("  - Team members: 8")
    print("\n[OK] Ready to start the application!")


def drop_all_tables():
    """Drop all tables (use with caution!)."""
    print("[WARNING] This will drop all tables!")
    confirm = input("Type 'yes' to confirm: ")

    if confirm.lower() == 'yes':
        sync_db_url = settings.database_url.replace('+asyncpg', '')
        engine = create_engine(sync_db_url, echo=False)

        print("[*] Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("[OK] All tables dropped!")
    else:
        print("[CANCELLED] Operation cancelled")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_all_tables()
    else:
        init_database()
