#!/usr/bin/env python3
"""Validate AnalysisProject CRUD API implementation."""
import sys
import asyncio
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test main API imports
        from omega_analysis.api.main import app
        print("✅ Main API imports successful")
        
        # Test v1 projects imports
        from omega_analysis.api.v1.projects import router
        print("✅ Projects router imports successful")
        
        # Test schemas
        from omega_analysis.api.v1.schemas import AnalysisProjectCreate, AnalysisProjectResponse
        print("✅ Schemas imports successful")
        
        # Test models
        from omega_analysis.models.analysis import AnalysisProject, ProjectStatus
        print("✅ Models imports successful")
        
        # Test logging and tracing
        from omega_analysis.logging import setup_logging
        from omega_analysis.tracing import setup_tracing
        print("✅ Logging and tracing imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_schema_validation():
    """Test Pydantic schema validation."""
    print("\nTesting schema validation...")
    
    try:
        from omega_analysis.api.v1.schemas import AnalysisProjectCreate
        from omega_analysis.models.analysis import SystemType
        
        # Test valid data
        valid_data = {
            "name": "Test Project",
            "description": "A test analysis project",
            "repository_url": "https://github.com/example/repo.git",
            "repository_branch": "main",
            "target_system_type": SystemType.SPRING_BOOT,
            "analysis_configuration": {"enable_static_analysis": True},
            "created_by": "test_user"
        }
        
        project = AnalysisProjectCreate(**valid_data)
        print("✅ Valid data schema validation successful")
        
        # Test invalid URL
        try:
            invalid_data = valid_data.copy()
            invalid_data["repository_url"] = "invalid-url"
            AnalysisProjectCreate(**invalid_data)
            print("❌ Invalid URL validation failed")
            return False
        except ValueError:
            print("✅ Invalid URL validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        return False


async def test_router_creation():
    """Test that router can be created successfully."""
    print("\nTesting router creation...")
    
    try:
        from omega_analysis.api.v1.projects import router
        
        # Check that router has expected routes
        routes = [route.path for route in router.routes]
        expected_routes = ["/", "/{project_id}", "/{project_id}/validate"]
        
        for expected_route in expected_routes:
            if expected_route not in routes:
                print(f"❌ Missing expected route: {expected_route}")
                return False
        
        print("✅ Router creation and route validation successful")
        return True
        
    except Exception as e:
        print(f"❌ Router creation error: {e}")
        return False


async def main():
    """Run all validation tests."""
    print("=== AnalysisProject CRUD API Validation ===\n")
    
    tests = [
        test_imports,
        test_schema_validation,
        test_router_creation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL VALIDATIONS PASSED")
        print("AnalysisProject CRUD API is ready for use!")
        return 0
    else:
        print(f"\n❌ {failed} validation(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())