"""
Utility functions for the ChaCC Dependency Manager.

Provides logging setup, hash calculations, and package management utilities.
"""

import hashlib
import logging
import subprocess
import sys
from typing import Set


default_logger = logging.getLogger('dependency_manager')
default_logger.setLevel(logging.INFO)
if not default_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(name)s - %(message)s')
    handler.setFormatter(formatter)
    default_logger.addHandler(handler)


def calculate_module_hash(module_name: str, requirements_content: str) -> str:
    """Calculate hash of a specific module's requirements."""
    content = f"{module_name}:{requirements_content}"
    return hashlib.sha256(content.encode()).hexdigest()


def calculate_combined_requirements_hash(module_hashes: dict[str, str]) -> str:
    """Calculate hash of all module requirement hashes combined."""
    sorted_hashes = sorted(module_hashes.items())
    combined = "|".join(f"{name}:{hash}" for name, hash in sorted_hashes)
    return hashlib.sha256(combined.encode()).hexdigest()


def get_installed_packages() -> Set[str]:
    """Get set of currently installed packages."""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'list', '--format=freeze'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            packages = set()
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    package_name = line.split('==')[0].lower()
                    packages.add(package_name)
            return packages
        else:
            default_logger.warning(f"Failed to get installed packages: {result.stderr}")
            return set()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        default_logger.warning(f"Error getting installed packages: {e}")
        return set()