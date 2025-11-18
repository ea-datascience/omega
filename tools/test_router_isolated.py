#!/usr/bin/env python3
"""Isolate the unhashable type list error."""
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_router_only():
    """Test just the router creation without dependencies."""
    try:
        from fastapi import APIRouter
        router = APIRouter()
        print("✅ Basic router creation successful")
        
        # Test the models import
        from omega_analysis.models.analysis import AnalysisProject
        print("✅ Models import successful")
        
        # Test the auth middleware import
        from omega_analysis.auth.middleware import require_scopes
        print("✅ Auth middleware import successful")
        
        # Test calling require_scopes
        # This might be where the error occurs
        try:
            scopes_dep = require_scopes("projects:read")
            print("✅ require_scopes call successful")
        except Exception as e:
            print(f"❌ require_scopes call failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_router_only()