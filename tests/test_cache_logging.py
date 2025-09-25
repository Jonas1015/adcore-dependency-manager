"""
Test script to check cache validation logging.
"""

import sys
import logging
import asyncio
sys.path.insert(0, 'src')

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(name)s - %(message)s')

from chacc.manager import DependencyManager

async def test_cache_validation():
    """Test cache validation with logging."""
    print("=== Testing Cache Validation Logging ===")

    dm = DependencyManager()

    test_cache = {
        'requirements_caches': {
            'requirements': {
                'hash': 'd74c1ab2abca00a7521c9a392384286a5655d0c8549c081a33656dbad58ba312',
                'packages': {'requests': '==2.25.1', 'urllib3': '==1.26.0'},
                'last_updated': '1234567890'
            }
        },
        'combined_hash': 'some_combined_hash',
        'resolved_packages': {'requests': '==2.25.1', 'urllib3': '==1.26.0'},
        'last_updated': '1234567890'
    }

    dm.save_cache(test_cache)
    print("Created test cache with packages:", list(test_cache['resolved_packages'].keys()))

    modules_requirements = None

    try:
        await dm.resolve_dependencies(modules_requirements=modules_requirements)
        print("✅ Cache validation completed")
    except Exception as e:
        print(f"❌ Error during cache validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cache_validation())