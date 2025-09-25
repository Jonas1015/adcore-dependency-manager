"""
Debug script to analyze caching issues with package detection.
"""

import sys
sys.path.insert(0, 'src')

from chacc.utils import get_installed_packages, canonicalize_name
from chacc.manager import DependencyManager

def debug_package_detection():
    """Debug why packages are not being detected as installed."""

    print("=== Package Detection Debug ===")

    installed = get_installed_packages()
    print(f"Found {len(installed)} installed packages (canonicalized)")
    print("Sample installed packages:", sorted(list(installed))[:10])

    dm = DependencyManager()

    test_cached_packages = {
        'build': '==1.3.0',
        'packaging': '==25.0',
        'pip': '==24.0',
        'pyproject-hooks': '==1.2.0'
    }

    print(f"\nTest cached packages: {test_cached_packages}")

    missing_packages = []
    for package_name, version_spec in test_cached_packages.items():
        canonical_name = canonicalize_name(package_name)
        if canonical_name not in installed:
            missing_packages.append(package_name)
            print(f"❌ Package '{package_name}' (canonical: '{canonical_name}') not found in installed packages")
        else:
            print(f"✅ Package '{package_name}' (canonical: '{canonical_name}') found in installed packages")

    print(f"\nMissing packages: {missing_packages}")

    if not missing_packages:
        print("\n🎉 All packages detected correctly with canonical name normalization!")
    else:
        print(f"\n⚠️  Still {len(missing_packages)} packages not detected - may need further investigation")

if __name__ == "__main__":
    debug_package_detection()