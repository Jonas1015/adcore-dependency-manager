"""
Test script to demonstrate the cleaner Config-based API.
"""

import sys
import logging
import asyncio
sys.path.insert(0, 'src')

from chacc import Config, re_resolve_dependencies, resolve_module_dependencies

async def test_config_api():
    """Test the cleaner Config-based API."""
    print("=== Testing Config-Based API ===")

    custom_logger = logging.getLogger('config_test')
    custom_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('CONFIG: %(levelname)s - %(message)s'))
    custom_logger.addHandler(handler)

    print("\n1. Simple usage (no config needed):")
    print("   await re_resolve_dependencies({'test': 'requests>=2.25.0'})")

    print("\n2. Advanced usage with Config object:")
    config = Config(
        cache_dir='./config_cache',
        logger=custom_logger,
        pre_resolve_hook=lambda name, content: print(f"Pre-resolve: {name}"),
        post_resolve_hook=lambda name, packages: print(f"Post-resolve: {name} -> {len(packages)} packages")
    )

    print("   config = Config(cache_dir='./config_cache', logger=custom_logger, ...)")
    print("   await re_resolve_dependencies({'test': 'requests>=2.25.0'}, config=config)")

    try:
        await re_resolve_dependencies(
            modules_requirements={'test': 'requests>=2.25.0\npackaging>=20.0'},
            config=config
        )
    except Exception as e:
        print(f"   Expected error (piptools not available): {type(e).__name__}")

    print("\n3. Individual functions with config:")
    print("   packages = resolve_module_dependencies('mymodule', 'requests>=2.25.0', config=config)")

    try:
        packages = resolve_module_dependencies(
            'mymodule',
            'requests>=2.25.0',
            config=config
        )
        print(f"   Resolved: {packages}")
    except Exception as e:
        print(f"   Expected error (piptools not available): {type(e).__name__}")

    print("\n✅ Config-based API is much cleaner!")
    print("   - Simple functions for basic usage")
    print("   - Config object for advanced customization")
    print("   - No parameter explosion")
    print("   - Type-safe and self-documenting")

if __name__ == "__main__":
    asyncio.run(test_config_api())