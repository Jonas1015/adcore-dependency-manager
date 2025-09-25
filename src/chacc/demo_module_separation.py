"""
Demonstrate how ChaCC separates dependencies by modules.
"""

import sys
import json
sys.path.insert(0, 'src')

from chacc import DependencyManager

def demo_module_separation():
    """Show how ChaCC caches dependencies separately per module."""
    print("=== ChaCC Module Separation Demo ===\n")

    dm = DependencyManager(cache_dir='./demo_cache')

    modules = {
        'web': 'fastapi>=0.100.0\nuvicorn[standard]>=0.20.0\npydantic>=2.0.0',
        'auth': 'passlib[bcrypt]>=1.7.0\npython-jose[cryptography]>=3.5.0\npython-multipart>=0.0.5',
        'database': 'sqlalchemy>=2.0.0\nalembic>=1.10.0\npsycopg2-binary>=2.9.0'
    }

    print("📦 Processing modules with separate dependencies:")
    for module_name, requirements in modules.items():
        print(f"\n🔍 Module: {module_name}")
        print(f"   Requirements: {requirements.replace(chr(10), ', ')}")

        packages = dm.resolve_module_dependencies(module_name, requirements)
        print(f"   Resolved {len(packages)} packages")

        sample_packages = list(packages.items())[:3]
        for pkg, version in sample_packages:
            print(f"     📋 {pkg}{version}")

    print("\n💾 Cache Structure (module separation):")
    cache = dm.load_cache()

    print("requirements_caches:")
    for module_name, module_cache in cache.get('requirements_caches', {}).items():
        packages = module_cache.get('packages', {})
        print(f"  📁 {module_name}: {len(packages)} packages")
        sample_pkgs = list(packages.items())[:2]
        for pkg, version in sample_pkgs:
            print(f"     └─ {pkg}{version}")

    print(f"\n📊 Combined resolved_packages: {len(cache.get('resolved_packages', {}))} total unique packages")

    print("\n✅ Key Benefits of Module Separation:")
    print("   • Each module's dependencies are cached separately")
    print("   • Only re-resolve when a specific module's requirements change")
    print("   • Can invalidate cache for individual modules")
    print("   • Clear visibility into which module needs which packages")

if __name__ == "__main__":
    demo_module_separation()