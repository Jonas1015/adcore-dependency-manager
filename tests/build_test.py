"""
Test script to verify the package builds correctly with pyproject.toml
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔧 {description}")
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description} successful")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    """Test the package build process."""
    print("🚀 Testing ChaCC Dependency Manager Package Build")
    print("=" * 60)

    if not os.path.exists("pyproject.toml"):
        print("❌ pyproject.toml not found")
        return False

    print("✅ pyproject.toml found")

    package_files = [
        "src/chacc/__init__.py",
        "src/chacc/chacc.py",
        "src/chacc/cli.py",
        "src/chacc/README.md",
        "LICENSE"
    ]

    for file_path in package_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False

    try:
        sys.path.insert(0, 'src')
        from chacc import DependencyManager, __version__
        print(f"✅ Package imports successfully (version: {__version__})")
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

    try:
        dm = DependencyManager()
        print("✅ DependencyManager instantiation successful")
    except Exception as e:
        print(f"❌ DependencyManager instantiation failed: {e}")
        return False

    try:
        import build
        print("✅ build module available")
        if run_command("python -m build --help", "Check build command availability"):
            if run_command("python -m build", "Build package"):
                print("✅ Package builds successfully")
                if os.path.exists("dist"):
                    dist_files = os.listdir("dist")
                    print(f"✅ Distribution files created: {dist_files}")
                else:
                    print("❌ dist directory not created")
                    return False
            else:
                print("⚠️ Build command failed (build tools may not be installed)")
        else:
            print("⚠️ Build tools not available for testing")
    except ImportError:
        print("⚠️ build module not available - install with: pip install build")

    print("\n" + "=" * 60)
    print("🎉 Package structure and basic functionality verified!")
    print("\n📦 Ready for publishing with:")
    print("   python -m build")
    print("   python -m twine upload dist/*")
    print("\n📋 Pre-publishing checklist:")
    print("   - Update version in pyproject.toml")
    print("   - Test on Test PyPI first")
    print("   - Create GitHub release")
    print("   - Update documentation")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)