"""Initialize or migrate the database schema."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import engine, init_db
from app.models.db_models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all tables in the database."""
    logger.info("Creating database tables...")
    
    try:
        # Create all tables
        init_db()
        
        logger.info("✅ Database tables created successfully!")
        logger.info(f"Database location: {engine.url}")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"\nCreated {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def drop_all_tables():
    """Drop all tables (WARNING: destructive operation)."""
    logger.warning("⚠️  WARNING: This will delete ALL data in the database!")
    confirm = input("Type 'YES' to confirm: ")
    
    if confirm != "YES":
        logger.info("Operation cancelled.")
        return False
    
    logger.info("Dropping all tables...")
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped successfully!")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {str(e)}")
        return False


def reset_database():
    """Drop and recreate all tables."""
    logger.info("Resetting database...")
    
    if drop_all_tables():
        return create_tables()
    
    return False


def check_database():
    """Check database status and list tables."""
    from sqlalchemy import inspect
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"\n📊 Database Status:")
        logger.info(f"Database URL: {engine.url}")
        logger.info(f"Tables: {len(tables)}")
        
        if tables:
            logger.info("\nExisting tables:")
            for table in tables:
                columns = inspector.get_columns(table)
                logger.info(f"  - {table} ({len(columns)} columns)")
        else:
            logger.info("\n⚠️  No tables found. Run 'init' to create tables.")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to check database: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management script for LEGID")
    parser.add_argument(
        "command",
        choices=["init", "reset", "check", "drop"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        create_tables()
    elif args.command == "reset":
        reset_database()
    elif args.command == "check":
        check_database()
    elif args.command == "drop":
        drop_all_tables()
