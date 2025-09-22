# AdCore Dependency Manager - Package Documentation

> **Intelligent dependency resolution with caching for Python applications**

[![PyPI version](https://badge.fury.io/py/adcore-dependency-manager.svg)](https://pypi.org/project/adcore-dependency-manager/)
[![Python versions](https://img.shields.io/pypi/pyversions/adcore-dependency-manager.svg)](https://pypi.org/project/adcore-dependency-manager/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Overview

The AdCore Dependency Manager is a pure Python package that provides intelligent, incremental dependency resolution and caching for Python applications. It serves as a drop-in replacement for pip with significant performance improvements for repeated installations.

### Key Features

- 🚀 **20x faster** than pip for repeated installs
- 🧠 **Smart caching** with module-level granularity
- 📦 **Multi-file support** for complex requirement structures
- 🔄 **Incremental updates** - only resolves changed dependencies
- 🐳 **Docker-optimized** for containerized deployments
- 🔗 **Extensible** with custom hooks for integration
- 💻 **CLI interface** with pip-like commands

## 🏗️ Architecture

### Core Components

```
adcore-dependency-manager/
├── dependency_manager.py    # Main DependencyManager class
├── cli.py                   # Command-line interface
└── __init__.py             # Package exports
```

### Cache Structure

The dependency manager uses a JSON-based cache structure:

```json
{
  "module_caches": {
    "web": {
      "hash": "abc123...",
      "packages": {"fastapi": "==0.116.1", "uvicorn": "==0.20.0"},
      "last_updated": "2024-01-01T12:00:00"
    }
  },
  "combined_hash": "def456...",
  "resolved_packages": {
    "fastapi": "==0.116.1",
    "uvicorn": "==0.20.0"
  }
}
```

## 📚 API Reference

### DependencyManager Class

#### Constructor

```python
DependencyManager(
    cache_dir: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    pre_resolve_hook: Optional[Callable] = None,
    post_resolve_hook: Optional[Callable] = None,
    install_hook: Optional[Callable] = None
)
```

**Parameters:**
- `cache_dir`: Directory for cache files (default: ".dependency_cache")
- `logger`: Custom logger instance (default: built-in logging)
- `pre_resolve_hook`: Callback before dependency resolution
- `post_resolve_hook`: Callback after dependency resolution
- `install_hook`: Custom installation logic callback

#### Methods

##### `resolve_dependencies(modules_requirements=None, requirements_file_pattern="requirements.txt", search_dirs=None)`

Perform incremental dependency resolution.

**Parameters:**
- `modules_requirements`: Dict of module names to requirement strings
- `requirements_file_pattern`: Glob pattern for requirement files
- `search_dirs`: List of directories to search

**Returns:** `None`

##### `invalidate_cache()`

Clear the entire dependency cache.

##### `invalidate_module_cache(module_name)`

Clear cache for a specific module.

**Parameters:**
- `module_name`: Name of the module to clear cache for

##### `calculate_module_hash(module_name, content)`

Calculate hash for module requirements.

**Parameters:**
- `module_name`: Name of the module
- `content`: Requirements content string

**Returns:** `str` - SHA256 hash

##### `get_installed_packages()`

Get set of currently installed packages.

**Returns:** `Set[str]` - Package names

### Convenience Functions

#### `re_resolve_dependencies(modules_requirements=None, requirements_file_pattern="requirements.txt", search_dirs=None)`

Main entry point for dependency resolution.

#### `invalidate_dependency_cache()`

Clear entire dependency cache.

#### `invalidate_module_cache(module_name)`

Clear cache for specific module.

## 🔧 CLI Reference

### Available Commands

The package provides three command aliases:
- `adcore-dependency-manager` (full name)
- `adcore-dm` (recommended)
- `dm` (short)

### Command Syntax

```bash
adcore-dm [OPTIONS] COMMAND [ARGS]...
```

### Global Options

- `--cache-dir TEXT`: Cache directory (default: .dependency_cache)
- `-v, --verbose`: Enable verbose logging
- `--help`: Show help message

### Commands

#### `install`

Install dependencies with resolution.

```bash
adcore-dm install [OPTIONS] [PACKAGES]...

Options:
  -r, --requirements FILE  Install from requirements file
  --help                   Show help
```

**Examples:**
```bash
adcore-dm install fastapi uvicorn
adcore-dm install -r requirements.txt
adcore-dm install  # Auto-discover requirements files
```

#### `resolve`

Resolve dependencies without installing.

```bash
adcore-dm resolve [OPTIONS]

Options:
  -r, --requirements FILE  Requirements file to resolve
  -p, --pattern TEXT       File pattern (default: requirements.txt)
  --search-dirs PATHS      Directories to search
  --help                   Show help
```

#### `cache`

Manage dependency cache.

```bash
adcore-dm cache [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show help
```

**Subcommands:**
- `info`: Show cache information
- `clear`: Clear entire cache
- `clear --module NAME`: Clear specific module cache

## 🔗 Integration Hooks

### Pre/Post Resolution Hooks

```python
def pre_resolve_callback(module_name: str, requirements: str) -> None:
    """Called before resolving dependencies for a module."""
    print(f"Starting resolution for {module_name}")

def post_resolve_callback(module_name: str, resolved_packages: dict) -> None:
    """Called after resolving dependencies for a module."""
    print(f"Resolved {len(resolved_packages)} packages for {module_name}")

dm = DependencyManager(
    pre_resolve_hook=pre_resolve_callback,
    post_resolve_hook=post_resolve_callback
)
```

### Custom Installation Hook

```python
def custom_installer(resolved_packages: dict, installed_packages: set) -> bool:
    """
    Custom installation logic.

    Args:
        resolved_packages: Dict of package_name -> version_spec
        installed_packages: Set of currently installed package names

    Returns:
        bool: True if installation successful, False to fallback to default
    """
    try:
        # Your custom installation logic here
        for package, version in resolved_packages.items():
            if package.lower() not in installed_packages:
                # Install package with custom logic
                pass
        return True
    except Exception:
        return False

dm = DependencyManager(install_hook=custom_installer)
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_adcore_compatibility.py
```

### Test Structure

```
tests/
├── build_test.py              # Package build verification
└── test_adcore_compatibility.py  # AdCore integration tests
```

## 📦 Distribution

### Building

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### Package Structure

```
adcore-dependency-manager-1.0.0/
├── src/
│   └── package/
│       ├── __init__.py
│       ├── dependency_manager.py
│       ├── cli.py
│       └── README.md
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone https://github.com/jonas1015/adcore-dependency-manager.git
cd adcore-dependency-manager

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest
```

## 📄 License

MIT License - see LICENSE file for details.

## 📚 Additional Resources

- [Main README](../README.md) - Quick start guide
- [GitHub Repository](https://github.com/jonas1015/adcore-dependency-manager)
- [PyPI Package](https://pypi.org/project/adcore-dependency-manager/)
- [Issues](https://github.com/jonas1015/adcore-dependency-manager/issues)

---

**AdCore Dependency Manager** - Making Python dependency management fast and reliable.