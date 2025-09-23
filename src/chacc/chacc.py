"""
Dependency Manager - Standalone Package

This module provides intelligent, incremental dependency resolution and caching
for Python packages in modular applications.

Features:
- Incremental dependency resolution (only resolve changed modules)
- Intelligent caching with module-level granularity
- Smart package installation (skip already installed)
- Automatic cache invalidation
- Conflict resolution between modules
- Configurable paths and logging
- Extensible with custom hooks for integration
- Works with any Python framework (FastAPI, Django, Flask, etc.)
- Pure Python implementation with no external dependencies

The package can be extended with custom hooks for integration with other systems
like ChaCC API Platform, allowing custom logging, installation logic, and
pre/post-processing of dependency resolution.
"""

import os
import json
import hashlib
import subprocess
import logging
import glob
from typing import Dict, Set, Optional, Callable, Any, List


default_logger = logging.getLogger('dependency_manager')
default_logger.setLevel(logging.INFO)
if not default_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(name)s - %(message)s')
    handler.setFormatter(formatter)
    default_logger.addHandler(handler)


class DependencyManager:
    """
    Manages Python package dependencies for modular applications.

    Provides incremental dependency resolution, caching, and intelligent
    package installation to optimize performance in development and production.

    This is a pure dependency management tool that works with requirements files
    and does not have any external dependencies. It can be extended with custom
    hooks for integration with other systems.

    Args:
        cache_dir: Directory for dependency cache files (default: ".dependency_cache")
        logger: Logger instance to use (default: built-in logging)
        pre_resolve_hook: Optional callback called before dependency resolution
        post_resolve_hook: Optional callback called after dependency resolution
        install_hook: Optional callback for custom package installation logic
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        pre_resolve_hook: Optional[Callable[[str, str], None]] = None,
        post_resolve_hook: Optional[Callable[[str, Dict[str, str]], None]] = None,
        install_hook: Optional[Callable[[Dict[str, str], Set[str]], bool]] = None
    ):
        """Initialize the dependency manager with configurable paths and hooks."""
        self.cache_dir = cache_dir or ".dependency_cache"
        self.cache_file = os.path.join(self.cache_dir, "dependency_cache.json")

        self.logger = logger or default_logger

        self.pre_resolve_hook = pre_resolve_hook
        self.post_resolve_hook = post_resolve_hook
        self.install_hook = install_hook

        os.makedirs(self.cache_dir, exist_ok=True)

    def calculate_module_hash(self, module_name: str, requirements_content: str) -> str:
        """Calculate hash of a specific module's requirements."""
        content = f"{module_name}:{requirements_content}"
        return hashlib.sha256(content.encode()).hexdigest()

    def calculate_combined_requirements_hash(self, module_hashes: Dict[str, str]) -> str:
        """Calculate hash of all module requirement hashes combined."""
        sorted_hashes = sorted(module_hashes.items())
        combined = "|".join(f"{name}:{hash}" for name, hash in sorted_hashes)
        return hashlib.sha256(combined.encode()).hexdigest()

    def load_cache(self) -> Dict:
        """Load dependency cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    if 'module_caches' not in cache:
                        cache['module_caches'] = {}
                    if 'combined_hash' not in cache:
                        cache['combined_hash'] = None
                    return cache
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Failed to load dependency cache: {e}")
        return {
            'module_caches': {},
            'backbone_hash': None,
            'combined_hash': None,
            'resolved_packages': {},
            'last_updated': None
        }

    def save_cache(self, cache_data: Dict):
        """Save dependency cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            self.logger.error(f"Failed to save dependency cache: {e}")

    def get_installed_packages(self) -> Set[str]:
        """Get set of currently installed packages."""
        try:
            result = subprocess.run([
                'python', '-m', 'pip', 'list', '--format=freeze'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                packages = set()
                for line in result.stdout.strip().split('\n'):
                    if '==' in line:
                        package_name = line.split('==')[0].lower()
                        packages.add(package_name)
                return packages
            else:
                self.logger.warning(f"Failed to get installed packages: {result.stderr}")
                return set()
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            self.logger.warning(f"Error getting installed packages: {e}")
            return set()

    def resolve_module_dependencies(self, module_name: str, requirements_content: str) -> Dict[str, str]:
        """Resolve dependencies for a specific module."""
        self.logger.info(f"Resolving dependencies for module: {module_name}")

        if self.pre_resolve_hook:
            try:
                self.pre_resolve_hook(module_name, requirements_content)
            except Exception as e:
                self.logger.warning(f"Pre-resolve hook failed: {e}")

        temp_req_file = os.path.join(os.path.dirname(self.cache_file), f"temp_{module_name}_requirements.txt")

        try:
            with open(temp_req_file, "w") as f:
                f.write(requirements_content)

            result = subprocess.run([
                'python', '-m', 'piptools', 'compile',
                '--output-file', f"{temp_req_file}.lock",
                '--allow-unsafe',
                temp_req_file
            ], capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"Failed to resolve dependencies for {module_name}: {result.stderr}")
                return {}

            resolved_packages = {}
            lock_file = f"{temp_req_file}.lock"
            if os.path.exists(lock_file):
                with open(lock_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '==' in line:
                            parts = line.split('==')
                            if len(parts) >= 2:
                                package_name = parts[0]
                                version = parts[1]
                                resolved_packages[package_name] = f"=={version}"

            self.logger.info(f"Resolved {len(resolved_packages)} packages for {module_name}")

            if self.post_resolve_hook:
                try:
                    self.post_resolve_hook(module_name, resolved_packages)
                except Exception as e:
                    self.logger.warning(f"Post-resolve hook failed: {e}")

            return resolved_packages

        except Exception as e:
            self.logger.error(f"Error resolving dependencies for {module_name}: {e}")
            return {}
        finally:
            for file in [temp_req_file, f"{temp_req_file}.lock"]:
                if os.path.exists(file):
                    os.remove(file)

    def merge_resolved_packages(self, *package_dicts: Dict[str, str]) -> Dict[str, str]:
        """Merge multiple resolved package dictionaries, resolving conflicts."""
        merged = {}

        for package_dict in package_dicts:
            for package_name, version_spec in package_dict.items():
                if package_name in merged:
                    existing_version = merged[package_name]
                    if version_spec != existing_version:
                        self.logger.warning(f"Version conflict for {package_name}: {existing_version} vs {version_spec}, using {version_spec}")
                merged[package_name] = version_spec

        return merged

    def install_missing_packages(self, resolved_packages: Dict[str, str], installed_packages: Set[str]):
        """Install only packages that are not already installed."""
        if self.install_hook:
            try:
                success = self.install_hook(resolved_packages, installed_packages)
                if success:
                    self.logger.info("Custom installation hook completed successfully")
                    return
                else:
                    self.logger.warning("Custom installation hook failed, falling back to default")
            except Exception as e:
                self.logger.warning(f"Custom installation hook failed: {e}, falling back to default")

        
        packages_to_install = []

        for package_name, version_spec in resolved_packages.items():
            package_name_lower = package_name.lower()
            if package_name_lower not in installed_packages:
                packages_to_install.append(f"{package_name}{version_spec}")
            else:
                self.logger.debug(f"Package {package_name} already installed, skipping")

        if packages_to_install:
            self.logger.info(f"Installing {len(packages_to_install)} missing packages...")
            try:
                batch_size = 50
                for i in range(0, len(packages_to_install), batch_size):
                    batch = packages_to_install[i:i + batch_size]
                    result = subprocess.run([
                        'python', '-m', 'pip', 'install', '--quiet'
                    ] + batch, capture_output=True, text=True, timeout=300)

                    if result.returncode != 0:
                        self.logger.error(f"Failed to install package batch: {result.stderr}")
                        raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

                self.logger.info("Package installation completed successfully")
            except subprocess.TimeoutExpired:
                self.logger.error("Package installation timed out")
                raise
        else:
            self.logger.info("All required packages are already installed")

    def invalidate_cache(self):
        """Invalidate the entire dependency cache."""
        try:
            cache_data = {
                'module_caches': {},
                'backbone_hash': None,
                'combined_hash': None,
                'resolved_packages': {},
                'last_updated': None
            }
            self.save_cache(cache_data)
            self.logger.info("Dependency cache invalidated")
        except Exception as e:
            self.logger.warning(f"Failed to invalidate dependency cache: {e}")
            if os.path.exists(self.cache_file):
                try:
                    os.remove(self.cache_file)
                    self.logger.info("Dependency cache file removed")
                except IOError as e2:
                    self.logger.error(f"Failed to remove dependency cache file: {e2}")

    def invalidate_module_cache(self, module_name: str):
        """Invalidate cache for a specific module."""
        try:
            cache = self.load_cache()
            if module_name in cache.get('module_caches', {}):
                del cache['module_caches'][module_name]
                cache['combined_hash'] = None
                self.save_cache(cache)
                self.logger.info(f"Cache invalidated for module: {module_name}")
        except Exception as e:
            self.logger.warning(f"Failed to invalidate cache for module {module_name}: {e}")

    async def resolve_dependencies(
        self,
        modules_requirements: Optional[Dict[str, str]] = None,
        requirements_file_pattern: str = "requirements.txt",
        search_dirs: Optional[List[str]] = None
    ):
        """
        Perform incremental dependency resolution for requirements.

        This method:
        1. Checks which requirements have changed
        2. Only resolves dependencies for changed requirements
        3. Merges results with cached dependencies
        4. Installs only missing packages

        Args:
            modules_requirements: Dict of name -> requirements_content
                                 If None, auto-discovers from filesystem
            requirements_file_pattern: Glob pattern for requirements files (default: "requirements.txt")
            search_dirs: List of directories to search for requirements files (default: current dir)
        """
        self.logger.info("Starting incremental dependency resolution...")

        if modules_requirements:
            requirements_to_process = list(modules_requirements.items())
        else:
            requirements_to_process = []
            search_dirs = search_dirs or ["."]

            for base_dir in search_dirs:
                if os.path.exists(base_dir):
                    pattern = os.path.join(base_dir, requirements_file_pattern)
                    req_files = glob.glob(pattern)

                    for req_file in req_files:
                        try:
                            with open(req_file, 'r') as f:
                                req_content = f.read().strip()

                            if req_content:
                                filename = os.path.basename(req_file)
                                req_name = os.path.splitext(filename)[0]
                                requirements_to_process.append((req_name, req_content))
                                self.logger.info(f"Discovered requirements file: {req_file}")

                        except Exception as e:
                            self.logger.warning(f"Failed to read requirements file {req_file}: {e}")

            if not requirements_to_process:
                self.logger.info(f"No requirements files found matching pattern: {requirements_file_pattern} in {search_dirs}")
                return

        try:
            cache = self.load_cache()
            req_caches = cache.get('requirements_caches', {})

            current_req_hashes = {}
            requirements_needing_resolution = []

            for req_name, req_content in requirements_to_process:
                req_hash = self.calculate_module_hash(req_name, req_content)
                current_req_hashes[req_name] = req_hash

                if req_name not in req_caches or req_caches[req_name].get('hash') != req_hash:
                    requirements_needing_resolution.append((req_name, req_content))
                    self.logger.info(f"Requirements '{req_name}' have changed")

            if not requirements_needing_resolution:
                self.logger.info("Using cached dependency resolution (no changes detected)")
                cached_packages = cache.get('resolved_packages', {})
                if cached_packages:
                    installed_packages = self.get_installed_packages()
                    self.install_missing_packages(cached_packages, installed_packages)
                else:
                    self.logger.warning("Cache is empty, performing full resolution")
                    requirements_needing_resolution = requirements_to_process
            else:
                self.logger.info(f"Resolving dependencies for {len(requirements_needing_resolution)} changed requirements")

            if requirements_needing_resolution:
                resolved_packages = {}
                for req_name, req_content in requirements_needing_resolution:
                    if req_content.strip():
                        req_packages = self.resolve_module_dependencies(req_name, req_content)
                        resolved_packages.update(req_packages)

                    req_caches[req_name] = {
                        'hash': current_req_hashes.get(req_name),
                        'packages': req_packages if req_content.strip() else {},
                        'last_updated': str(os.path.getmtime(os.path.join(self.cache_dir, '..')))  # Rough timestamp
                    }

                cached_packages = {}
                for req_name, req_cache in req_caches.items():
                    if req_name not in [r[0] for r in requirements_needing_resolution]:
                        cached_packages.update(req_cache.get('packages', {}))

                all_resolved_packages = self.merge_resolved_packages(cached_packages, resolved_packages)

                installed_packages = self.get_installed_packages()
                self.install_missing_packages(all_resolved_packages, installed_packages)

                combined_hash = self.calculate_combined_requirements_hash(current_req_hashes)
                cache_data = {
                    'requirements_caches': req_caches,
                    'combined_hash': combined_hash,
                    'resolved_packages': all_resolved_packages,
                    'last_updated': str(os.path.getmtime(self.cache_dir)) if os.path.exists(self.cache_dir) else None
                }
                self.save_cache(cache_data)
                self.logger.info("Dependency cache updated with incremental changes")

            self.logger.info("Incremental dependency resolution completed successfully")

        except Exception as e:
            self.logger.error(f"Error during dependency resolution: {e}", exc_info=True)
            raise


dependency_manager = DependencyManager()


def calculate_module_hash(module_name: str, requirements_content: str) -> str:
    """Calculate hash of a specific module's requirements."""
    return dependency_manager.calculate_module_hash(module_name, requirements_content)


def calculate_combined_requirements_hash(module_hashes: Dict[str, str]) -> str:
    """Calculate hash of all module requirement hashes combined."""
    return dependency_manager.calculate_combined_requirements_hash(module_hashes)


def load_dependency_cache() -> Dict:
    """Load dependency cache from file."""
    return dependency_manager.load_cache()


def save_dependency_cache(cache_data: Dict):
    """Save dependency cache to file."""
    dependency_manager.save_cache(cache_data)


def get_installed_packages() -> Set[str]:
    """Get set of currently installed packages."""
    return dependency_manager.get_installed_packages()


def resolve_module_dependencies(module_name: str, requirements_content: str) -> Dict[str, str]:
    """Resolve dependencies for a specific module."""
    return dependency_manager.resolve_module_dependencies(module_name, requirements_content)


def merge_resolved_packages(*package_dicts: Dict[str, str]) -> Dict[str, str]:
    """Merge multiple resolved package dictionaries, resolving conflicts."""
    return dependency_manager.merge_resolved_packages(*package_dicts)


def install_missing_packages(resolved_packages: Dict[str, str], installed_packages: Set[str]):
    """Install only packages that are not already installed."""
    dependency_manager.install_missing_packages(resolved_packages, installed_packages)


def invalidate_dependency_cache():
    """Invalidate the dependency cache."""
    dependency_manager.invalidate_cache()


def invalidate_module_cache(module_name: str):
    """Invalidate cache for a specific module."""
    dependency_manager.invalidate_module_cache(module_name)


async def re_resolve_dependencies(
    modules_requirements: Optional[Dict[str, str]] = None,
    requirements_file_pattern: str = "requirements.txt",
    search_dirs: Optional[List[str]] = None
):
    """Re-resolve and reinstall all dependencies."""
    await dependency_manager.resolve_dependencies(modules_requirements, requirements_file_pattern, search_dirs)