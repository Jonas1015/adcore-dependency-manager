"""
Show ChaCC's module-based cache structure.
"""

import sys
import json
sys.path.insert(0, 'src')

from chacc import DependencyManager

def demo_cache_structure():
    """Show how ChaCC structures cache by modules."""
    print("=== ChaCC Module-Based Cache Structure ===\n")

    dm = DependencyManager(cache_dir='./demo_cache')

    simulated_cache = {
        'requirements_caches': {
            'web': {
                'hash': 'abc123_web_hash',
                'packages': {
                    'fastapi': '==0.104.1',
                    'uvicorn': '==0.24.0',
                    'pydantic': '==2.5.0',
                    'starlette': '==0.27.0',
                    'uvicorn[standard]': '==0.24.0'
                },
                'last_updated': '2024-01-01T10:00:00'
            },
            'auth': {
                'hash': 'def456_auth_hash',
                'packages': {
                    'passlib[bcrypt]': '==1.7.4',
                    'python-jose[cryptography]': '==3.5.0',
                    'python-multipart': '==0.0.6',
                    'bcrypt': '==4.0.1',
                    'cryptography': '==41.0.7'
                },
                'last_updated': '2024-01-01T10:05:00'
            },
            'database': {
                'hash': 'ghi789_db_hash',
                'packages': {
                    'sqlalchemy': '==2.0.23',
                    'alembic': '==1.13.1',
                    'psycopg2-binary': '==2.9.9',
                    'typing-extensions': '==4.9.0',
                    'greenlet': '==3.0.3'
                },
                'last_updated': '2024-01-01T10:10:00'
            }
        },
        'combined_hash': 'combined_xyz_hash',
        'resolved_packages': {
            'fastapi': '==0.104.1',
            'uvicorn': '==0.24.0',
            'pydantic': '==2.5.0',
            'starlette': '==0.27.0',
            'uvicorn[standard]': '==0.24.0',
            'passlib[bcrypt]': '==1.7.4',
            'python-jose[cryptography]': '==3.5.0',
            'python-multipart': '==0.0.6',
            'bcrypt': '==4.0.1',
            'cryptography': '==41.0.7',
            'sqlalchemy': '==2.0.23',
            'alembic': '==1.13.1',
            'psycopg2-binary': '==2.9.9',
            'typing-extensions': '==4.9.0',
            'greenlet': '==3.0.3'
        },
        'last_updated': '2024-01-01T10:10:00'
    }

    dm.save_cache(simulated_cache)
    loaded_cache = dm.load_cache()

    print("📂 Cache Structure by Module:")
    print("=" * 50)

    req_caches = loaded_cache.get('requirements_caches', {})
    for module_name, module_data in req_caches.items():
        packages = module_data.get('packages', {})
        print(f"\n🔹 Module: {module_name}")
        print(f"   📋 Hash: {module_data.get('hash', 'N/A')[:12]}...")
        print(f"   📦 Packages: {len(packages)}")
        print("   📅 Last Updated: {}".format(module_data.get('last_updated', 'N/A')))

        # Show first 3 packages for this module
        print("   📋 Sample packages:")
        for i, (pkg, version) in enumerate(list(packages.items())[:3]):
            print(f"      {i+1}. {pkg}{version}")
        if len(packages) > 3:
            print(f"      ... and {len(packages) - 3} more")

    print(f"\n📊 Combined View:")
    print(f"   🎯 Total unique packages: {len(loaded_cache.get('resolved_packages', {}))}")
    print(f"   📁 Total modules cached: {len(req_caches)}")
    print(f"   🔄 Combined hash: {loaded_cache.get('combined_hash', 'N/A')[:12]}...")

    print("\n✅ Module Separation Benefits:")
    print("   • Each module has its own cache entry")
    print("   • Individual module cache invalidation")
    print("   • Only re-resolve changed modules")
    print("   • Clear dependency ownership tracking")
    print("   • Supports modular application architecture")

    print("\n🔧 Available Operations:")
    print("   • dm.invalidate_module_cache('web') - Clear only web module")
    print("   • dm.invalidate_cache() - Clear all modules")
    print("   • Individual module resolution tracking")

if __name__ == "__main__":
    demo_cache_structure()