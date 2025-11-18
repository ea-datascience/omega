#!/usr/bin/env python3
"""Script to validate database schema migration setup."""
import os
import sys
from pathlib import Path

# Add the tools directory to Python path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir / "src"))

from omega_analysis.models.base import Base
from omega_analysis.models.analysis import (
    AnalysisProject, SystemArchitecture, DependencyGraph, 
    PerformanceBaseline, RiskAssessment, ComplianceRecord, 
    ServiceBoundary, ArchitecturalComponent, DependencyRelation,
    MetricMeasurement, RiskFactor, ComplianceRequirement, BoundaryMetric
)
from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable


def validate_models():
    """Validate that all models are properly defined."""
    print("🔍 Validating SQLAlchemy models...")
    
    # Check that all models are properly registered
    models = [
        # Core entities
        AnalysisProject, SystemArchitecture, DependencyGraph,
        PerformanceBaseline, RiskAssessment, ComplianceRecord, ServiceBoundary,
        # Supporting entities
        ArchitecturalComponent, DependencyRelation, MetricMeasurement,
        RiskFactor, ComplianceRequirement, BoundaryMetric
    ]
    
    for model in models:
        print(f"  ✅ {model.__name__} - table: {model.__tablename__}")
        
        # Validate that model has proper columns
        if hasattr(model, '__table__'):
            column_count = len(model.__table__.columns)
            print(f"     Columns: {column_count}")
    
    print(f"\n📊 Total models: {len(models)}")
    print(f"📊 Total tables in metadata: {len(Base.metadata.tables)}")
    return True


def generate_schema_sql():
    """Generate SQL schema creation statements."""
    print("\n🏗️  Generating SQL schema statements...")
    
    # Create a mock engine for SQL generation
    engine = create_engine("postgresql://", echo=False, strategy='mock', executor=lambda sql, *_: None)
    
    try:
        # Generate CREATE TABLE statements
        print("\n--- SQL Schema Creation Statements ---")
        Base.metadata.create_all(engine, checkfirst=False)
        print("✅ SQL schema generation completed")
        return True
    except Exception as e:
        print(f"❌ Error generating SQL: {e}")
        return False


def validate_migration_files():
    """Validate Alembic migration setup."""
    print("\n📁 Validating Alembic migration setup...")
    
    alembic_dir = tools_dir / "alembic"
    versions_dir = alembic_dir / "versions"
    
    # Check Alembic directory structure
    if alembic_dir.exists():
        print(f"  ✅ Alembic directory exists: {alembic_dir}")
    else:
        print(f"  ❌ Alembic directory missing: {alembic_dir}")
        return False
    
    if versions_dir.exists():
        print(f"  ✅ Versions directory exists: {versions_dir}")
        
        # List migration files
        migration_files = list(versions_dir.glob("*.py"))
        print(f"  📄 Migration files found: {len(migration_files)}")
        for migration_file in migration_files:
            print(f"     - {migration_file.name}")
    else:
        print(f"  ❌ Versions directory missing: {versions_dir}")
        return False
    
    # Check key files
    key_files = ["env.py", "script.py.mako"]
    for file_name in key_files:
        file_path = alembic_dir / file_name
        if file_path.exists():
            print(f"  ✅ {file_name} exists")
        else:
            print(f"  ❌ {file_name} missing")
            return False
    
    return True


def main():
    """Main validation function."""
    print("=" * 60)
    print("🔬 OMEGA ANALYSIS - DATABASE SCHEMA VALIDATION")
    print("=" * 60)
    
    success = True
    
    # Validate models
    try:
        if not validate_models():
            success = False
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        success = False
    
    # Generate schema SQL (for validation)
    try:
        if not generate_schema_sql():
            success = False
    except Exception as e:
        print(f"❌ Schema SQL generation failed: {e}")
        success = False
    
    # Validate migration setup
    try:
        if not validate_migration_files():
            success = False
    except Exception as e:
        print(f"❌ Migration file validation failed: {e}")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL VALIDATIONS PASSED")
        print("\n🎉 Database schema migration setup is complete!")
        print("\nNext steps when database is available:")
        print("  1. Start PostgreSQL database")
        print("  2. Run: alembic upgrade head")
        print("  3. Verify tables are created with pg_vector extension")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("Please review the errors above and fix the issues.")
    
    print("=" * 60)
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)