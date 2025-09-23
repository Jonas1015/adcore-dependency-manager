# ChaCC Dependency Manager

Intelligent, incremental dependency resolution and caching for Python applications.

## Features

- **Smart Caching**: Only resolves changed dependencies
- **Multi-file Support**: Handles complex requirement structures
- **Incremental Updates**: No full reinstalls
- **Docker-optimized**: Layer caching friendly

## Installation

```bash
pip install chacc-dependency-manager[resolver]
```

## Usage

```bash
cdm install -r requirements.txt
cdm resolve
cdm cache --info
```

## API

```python
from dependency_manager import DependencyManager

dm = DependencyManager()
await dm.resolve_dependencies()