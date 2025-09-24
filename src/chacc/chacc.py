"""
ChaCC Dependency Manager - Main module with convenience functions.

This module provides the main API and convenience functions for the ChaCC
dependency manager package. The core functionality is split across:

- manager.py: DependencyManager class and core logic
- utils.py: Utility functions and logging setup
- cli.py: Command-line interface
"""

from .manager import DependencyManager
from .utils import (
    calculate_module_hash,
    calculate_combined_requirements_hash,
    get_installed_packages
)


dependency_manager = DependencyManager()

def load_dependency_cache() -> dict:
    """Load dependency cache from file."""
    return dependency_manager.load_cache()

def save_dependency_cache(cache_data: dict):
    """Save dependency cache to file."""
    dependency_manager.save_cache(cache_data)

def resolve_module_dependencies(module_name: str, requirements_content: str) -> dict[str, str]:
    """Resolve dependencies for a specific module."""
    return dependency_manager.resolve_module_dependencies(module_name, requirements_content)


def merge_resolved_packages(*package_dicts: dict[str, str]) -> dict[str, str]:
    """Merge multiple resolved package dictionaries, resolving conflicts."""
    return dependency_manager.merge_resolved_packages(*package_dicts)


def install_missing_packages(resolved_packages: dict[str, str], installed_packages: set[str]):
    """Install only packages that are not already installed."""
    dependency_manager.install_missing_packages(resolved_packages, installed_packages)


def invalidate_dependency_cache():
    """Invalidate the dependency cache."""
    dependency_manager.invalidate_cache()


def invalidate_module_cache(module_name: str):
    """Invalidate cache for a specific module."""
    dependency_manager.invalidate_module_cache(module_name)


async def re_resolve_dependencies(
    modules_requirements: dict[str, str] | None = None,
    requirements_file_pattern: str = "requirements.txt",
    search_dirs: list[str] | None = None
):
    """Re-resolve and reinstall all dependencies."""
    await dependency_manager.resolve_dependencies(modules_requirements, requirements_file_pattern, search_dirs)