# ChaCC Dependency Manager Package

This package provides intelligent, incremental dependency resolution and caching for Python applications.

## Features

- **Incremental dependency resolution** - Only resolve changed modules
- **Intelligent caching** - Skip already installed packages
- **Multi-module support** - Handle complex modular applications
- **Pure Python** - No external dependencies required
- **Extensible** - Custom hooks for integration

## Usage

```python
from chacc import DependencyManager

dm = DependencyManager()
await dm.resolve_dependencies()
```

## CLI Usage

```bash
cdm install -r requirements.txt
cdm cache --info
```

## Architecture

The package consists of:
- `chacc.py` - Core dependency management logic
- `cli.py` - Command-line interface
- `__init__.py` - Package initialization

For more information, see the main project README.md.