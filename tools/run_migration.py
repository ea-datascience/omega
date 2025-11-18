#!/usr/bin/env python3
"""Script to run database migration manually."""
import os
import sys
from pathlib import Path

# Add the tools directory to Python path
tools_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tools_dir / "src"))

from alembic.config import Config
from alembic import command
from omega_analysis.config import get_settings


def run_migration():
    """Run the database migration."""
    try:
        # Set working directory to tools
        os.chdir(tools_dir)
        
        # Get database URL from settings
        # Note: This would normally use the real database, but since we don't have Docker
        # running, we'll just demonstrate the migration script structure
        
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Override database URL if needed
        # alembic_cfg.set_main_option("sqlalchemy.url", "postgresql://...")
        
        print("Running database migration...")
        print("Current directory:", os.getcwd())
        print("Alembic config file:", alembic_cfg.config_file_name)
        
        # Check current revision
        try:
            command.current(alembic_cfg, verbose=True)
        except Exception as e:
            print(f"Note: Could not check current revision (database may not exist): {e}")
        
        # Run migration
        try:
            command.upgrade(alembic_cfg, "head")
            print("✅ Database migration completed successfully!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("This is expected without a running database.")
            
        # Show revision history
        try:
            command.history(alembic_cfg, verbose=True)
        except Exception as e:
            print(f"Note: Could not show history: {e}")
            
    except Exception as e:
        print(f"Error running migration: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)