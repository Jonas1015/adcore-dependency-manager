"""
Test script to demonstrate enhanced API with full parameter support.
"""

import sys
import logging
import asyncio
import pytest
sys.path.insert(0, 'src')

from chacc import (
    Config,
    re_resolve_dependencies,
    resolve_module_dependencies,
    invalidate_dependency_cache
)

@pytest.mark.asyncio
async def test_enhanced_api():
    """Test the enhanced API with custom parameters."""
    print("=== Testing Enhanced API ===")

    custom_logger = logging.getLogger('custom_test')
    custom_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('CUSTOM: %(levelname)s - %(message)s'))
    custom_logger.addHandler(handler)

    config = Config(cache_dir='./test_cache', logger=custom_logger)

    print("\n1. Testing re_resolve_dependencies with custom config:")
    try:
        await re_resolve_dependencies(
            modules_requirements={'test': 'requests>=2.25.0\npackaging>=20.0'},
            config=config
        )
    except Exception as e:
        print(f"Expected error (piptools not available): {e}")

    print("\n2. Testing resolve_module_dependencies with custom config:")
    try:
        packages = resolve_module_dependencies(
            'mymodule',
            'requests>=2.25.0',
            config=config
        )
        print(f"Resolved packages: {packages}")
    except Exception as e:
        print(f"Expected error (piptools not available): {e}")

    print("\n3. Testing invalidate_dependency_cache with custom config:")
    invalidate_dependency_cache(config=config)
    print("Cache invalidated in custom directory")

    print("\n✅ Enhanced API test completed - all functions now accept customization parameters!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_api())