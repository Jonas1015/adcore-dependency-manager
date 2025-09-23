#!/usr/bin/env python3
"""
Test script to verify ChaCC API compatibility with the new dependency manager package.
This simulates how ChaCC uses the dependency manager.
"""

import sys
import os
sys.path.insert(0, 'src')

def test_chacc_compatibility():
    """Test that ChaCC can still use the dependency manager."""
    try:
        from package import chacc as dm

        invalidate_module_cache = dm.invalidate_module_cache
        re_resolve_dependencies = dm.re_resolve_dependencies
        DependencyManager = dm.DependencyManager
        print("✅ ChaCC imports successful")

        assert callable(invalidate_module_cache), "invalidate_module_cache should be callable"
        assert callable(re_resolve_dependencies), "re_resolve_dependencies should be callable"
        assert callable(DependencyManager), "DependencyManager should be callable"
        print("✅ All functions are callable")

        dm = DependencyManager()
        print("✅ DependencyManager instantiation successful")

        assert hasattr(dm, 'resolve_dependencies'), "Should have resolve_dependencies method"
        assert hasattr(dm, 'invalidate_cache'), "Should have invalidate_cache method"
        print("✅ DependencyManager has expected methods")

        import inspect
        sig = inspect.signature(re_resolve_dependencies)
        params = list(sig.parameters.keys())

        assert 'modules_requirements' in params, "Should accept modules_requirements parameter"
        assert 'requirements_file_pattern' in params, "Should accept requirements_file_pattern parameter"
        print("✅ re_resolve_dependencies has correct signature")

        print("\n🎉 All Module based apps compatibility tests passed!")
        return True

    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chacc_compatibility()
    sys.exit(0 if success else 1)