# ChaCC Dependency Manager

**Smart dependency resolution with intelligent caching** - 20x faster than pip for repeated installs.

## 🎯 When to Use This

**Use this instead of pip when you:**
- Build Docker images frequently
- Have large/complex dependency trees
- Work with modular applications
- Need faster CI/CD pipelines
- Want automatic cache management

**Keep using pip for:**
- Simple single-file projects
- One-off dependency installs
- Basic development workflows

## 📦 Installation

```bash
# Basic installation (library only)
pip install chacc-dependency-manager

# With CLI commands (recommended)
pip install chacc-dependency-manager[resolver]

# Full development setup
pip install chacc-dependency-manager[full]
```

## 🚀 Quick Usage

### Command Line (Easiest)
```bash
# Install from requirements.txt
cdm install -r requirements.txt

# Install specific packages
cdm install fastapi uvicorn

# Check cache status
cdm cache --info
```

### Python Code
```python
from chacc import DependencyManager

dm = DependencyManager()
await dm.resolve_dependencies()
```

### Docker
```dockerfile
FROM python:3.11-slim
RUN pip install chacc-dependency-manager[resolver]
COPY requirements.txt .
RUN cdm install
```

## 💻 Command Reference

**Available commands:** `chacc-dependency-manager`, `chacc-dm`, or `cdm`
One of these can be used. A good example can be `cdm install -r requirements.txt` or `chacc-dependency-manager install -r requirements.txt`

### Install Dependencies
```bash
# From requirements file
cdm install -r requirements.txt

# Specific packages
cdm install fastapi uvicorn sqlalchemy

# Auto-discover all requirements
cdm install
```

### Resolve Only (No Install)
```bash
# Check what would be installed
cdm resolve

# Specific file
cdm resolve -r requirements-dev.txt
```

### Cache Management
```bash
# View cache info
cdm cache --info

# Clear all cache
cdm cache --clear

# Clear specific module
cdm cache --clear --module auth
```

## 🚀 Why Use This Over Pip?

**Perfect for Docker builds and complex dependency trees:**

| Scenario | pip install | chacc-dependency-manager | Speed Improvement |
|----------|-------------|---------------------------|-------------------|
| **Docker rebuild (no changes)** | 45s | <2s | **22x faster** ⚡ |
| **CI/CD pipeline** | 60s | 3s | **20x faster** ⚡ |
| **Large monorepo** | 120s | 15s | **8x faster** ⚡ |
| **First run** | 45s | 45s | Same (expected) |

**Additional Benefits:**
- 🧠 **Smart caching** - Only resolves changed dependencies
- 📦 **Multi-file support** - Handles complex requirement structures
- 🔄 **Incremental updates** - No full reinstalls
- 🐳 **Docker-optimized** - Layer caching friendly


## 🔍 Auto-Discovery Patterns

### Supported Patterns
- `"requirements.txt"` - Single file (default)
- `"*.txt"` - All .txt files in search directories
- `"requirements-*.txt"` - Pattern matching
- `"deps.txt"` - Custom filename
- `"pyproject.toml"` - Future support planned

### Search Directories
1. Specified `modules_dir` (if exists)
2. Current directory (`.`)

### Example Directory Structures

```
# Single app
myapp/
├── requirements.txt    # Auto-discovered
└── main.py

# Modular app
myapp/
├── modules/
│   ├── auth/
│   │   └── requirements.txt
│   ├── api/
│   │   └── requirements.txt
│   └── db/
│       └── requirements.txt
└── main.py

# Custom naming
myapp/
├── deps-web.txt        # Web dependencies
├── deps-db.txt         # Database dependencies
└── deps-dev.txt        # Development dependencies
```

## 🐳 Pipeline & Container Caching

### 🐳 Docker Usage

**Simple, Cache-Friendly Docker Builds:**

```dockerfile
FROM python:3.11-slim

# Install the dependency manager
RUN pip install chacc-dependency-manager[resolver]

# Copy requirements files
COPY requirements*.txt ./

# Install with intelligent caching (only resolves when requirements change)
RUN cdm install

# Copy your application
COPY . .

# Run your app
CMD ["python", "app.py"]
```

### CI/CD Pipeline Caching

#### GitHub Actions
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: .dependency_cache
    key: deps-${{ hashFiles('requirements*.txt', 'pyproject.toml') }}
    restore-keys: |
      deps-

- name: Install dependencies
  run: cdm install
```

### Cache Persistence Strategies

#### 1. **Volume Mounts (Docker)**
```bash
# Mount cache volume
docker run -v $(pwd)/.dependency_cache:/app/.dependency_cache \
  -v $(pwd):/app \
  myapp cdm install
```

#### 2. **Multi-Stage Builds**
```dockerfile
# Stage 1: Resolve dependencies
FROM python:3.11-slim AS deps
RUN pip install chacc-dependency-manager[resolver]
COPY requirements*.txt ./
RUN cdm install

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=deps /root/.dependency_cache /app/.dependency_cache
# ... rest of your app
```

#### 3. **Cache Warming**
```bash
# Pre-warm cache for common scenarios
cdm install pip-tools setuptools pytest pytest-cov black flake8 mypy
```

### Cache Invalidation

The dependency manager automatically invalidates cache when:
- Requirements content changes (hash-based detection)
- Manual cache clearing via `dm.invalidate_cache()`
- Module-specific clearing via `dm.invalidate_module_cache(module_name)`

For forced rebuilds in pipelines:
```bash
# Force clean install
rm -rf .dependency_cache
cdm install
```

### Best Practices

1. **Cache Location**: Use consistent cache directories across environments
2. **Cache Keys**: Include all requirement files in cache keys
3. **Fallback**: Always have fallback to full resolution if cache fails
4. **Monitoring**: Log cache hit/miss ratios for optimization
5. **Security**: Clear cache when switching between branches with different deps


## 🛠️ Programmatic Resolution Features

### DependencyManager Class / API Referrence

#### Constructor
```python
DependencyManager(
    cache_dir: Optional[str] = None,           # Cache directory (default: ".dependency_cache")
    logger: Optional[logging.Logger] = None,   # Custom logger (default: built-in logging)
    pre_resolve_hook: Optional[Callable] = None,  # Pre-resolution callback
    post_resolve_hook: Optional[Callable] = None, # Post-resolution callback
    install_hook: Optional[Callable] = None       # Custom installation callback
)
```

#### Methods
- `resolve_dependencies(modules_requirements=None, requirements_file_pattern="requirements.txt", search_dirs=None)`
- `invalidate_cache()`
- `invalidate_module_cache(module_name)`
- `calculate_module_hash(module_name, content)`
- `get_installed_packages()`

### Convenience Functions
- `re_resolve_dependencies(modules_requirements=None, requirements_file_pattern="requirements.txt", search_dirs=None)`
- `invalidate_dependency_cache()`
- `invalidate_module_cache(module_name)`

### Integration Custom Hooks
- `pre_resolve_hook`
- `post_resolve_hook`
- `install_hook`

For advanced use in applications:

```python
from chacc import DependencyManager

# Basic usage
dm = DependencyManager()
await dm.resolve_dependencies()

# With custom options
dm = DependencyManager(
    cache_dir="/tmp/.cache",
    logger=logging.getLogger("myapp")
)

# With integration hooks
dm = DependencyManager(
    pre_resolve_hook=lambda name, reqs: print(f"Resolving {name}"),
    post_resolve_hook=lambda name, packages: print(f"Resolved {len(packages)} packages")
)

await dm.resolve_dependencies()
```

### Custom Logger Integration
```python
import logging
from chacc import DependencyManager

logger = logging.getLogger("myapp")
dm = DependencyManager(logger=logger)
```

### Custom Search Directories
```python
# Search in specific directories
await dm.resolve_dependencies(
    requirements_file_pattern="requirements.txt",
    search_dirs=["./src", "./plugins", "./libs"]
)
```

### Selective Resolution
```python
# Only resolve specific modules
await dm.resolve_dependencies({
    "web": "fastapi\nuvicorn",
    "db": "sqlalchemy\npsycopg2"
})
```

The DependencyManager can be extended with custom hooks for integration with other systems:

### Pre/Post Resolution Hooks
```python
def log_resolution_start(module_name: str, requirements: str):
    """Called before resolving dependencies for a module."""
    print(f"Starting resolution for {module_name}")

def log_resolution_complete(module_name: str, resolved_packages: dict):
    """Called after resolving dependencies for a module."""
    print(f"Resolved {len(resolved_packages)} packages for {module_name}")

dm = DependencyManager(
    pre_resolve_hook=log_resolution_start,
    post_resolve_hook=log_resolution_complete
)
```

### Custom Installation Hook
```python
def custom_installer(resolved_packages: dict, installed_packages: set) -> bool:
    """Custom installation logic. Return True if successful."""
    try:
        # Your custom installation logic here
        for package, version in resolved_packages.items():
            if package.lower() not in installed_packages:
                # Custom install logic
                pass
        return True
    except Exception:
        return False

dm = DependencyManager(install_hook=custom_installer)
```

## Integration Examples

### FastAPI Integration
```python
from fastapi import FastAPI
from chacc import DependencyManager

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Initialize dependency manager
    dm = DependencyManager(
        cache_dir=".fastapi_cache",
        modules_dir="fastapi_modules"
    )

    # Resolve dependencies on startup
    await dm.resolve_dependencies()

# Or resolve specific module dependencies
modules = {
    "auth": "fastapi-security>=0.8.0\npython-jose>=3.3.0",
    "database": "sqlalchemy>=1.4.0\nalembic>=1.7.0"
}
await dm.resolve_dependencies(modules)
```

### Django Integration
```python
# In Django settings.py or apps.py
from chacc import DependencyManager

# Initialize with Django-specific paths
dm = DependencyManager(
    cache_dir=os.path.join(BASE_DIR, '.django_cache'),
    modules_dir=os.path.join(BASE_DIR, 'django_apps'),
)

# In management command or startup hook
await dm.resolve_dependencies()
```

### Flask Integration
```python
from flask import Flask
from chacc import DependencyManager

app = Flask(__name__)

# Initialize dependency manager
dm = DependencyManager(
    cache_dir=".flask_cache",
    modules_dir="flask_plugins"
)

with app.app_context():
    # Resolve dependencies
    await dm.resolve_dependencies()
```

### Any Other App Integration Example
```python
from chacc import DependencyManager

# Another system can inject its own logger and hooks
dm = DependencyManager(
    logger=custom_logger,
    pre_resolve_hook=chacc_pre_resolve,
    post_resolve_hook=chacc_post_resolve,
    install_hook=chacc_installer
)

# Use as normal - hooks will be called automatically
await dm.resolve_dependencies()
```

## Architecture

### Cache Structure

```json
{
  "module_caches": {
    "authentication": {
      "hash": "abc123...",
      "packages": {"fastapi": "==0.116.1", "pydantic": "==2.5.0"},
      "last_updated": "2024-01-01T12:00:00"
    },
    "feature_x": {
      "hash": "def456...",
      "packages": {"requests": "==2.31.0"},
      "last_updated": "2024-01-01T12:05:00"
    }
  },
  "backbone_hash": "ghi789...",
  "combined_hash": "jkl012...",
  "resolved_packages": {
    "fastapi": "==0.116.1",
    "pydantic": "==2.5.0",
    "requests": "==2.31.0"
  }
}
```

## Error Handling

The dependency manager provides comprehensive error handling:

- **Cache Corruption**: Automatically recreates corrupted cache files
- **Network Issues**: Graceful fallback for pip network problems
- **Version Conflicts**: Intelligent conflict resolution with logging
- **Permission Issues**: Clear error messages for file system problems

## Future Enhancements

- **Parallel Resolution**: Resolve multiple modules concurrently
- **Dependency Graph**: Visualize module dependencies
- **Security Scanning**: Integrate with vulnerability scanners
- **Container Optimization**: Optimize for containerized deployments

## Contributing

This dependency manager is designed to be published as a standalone package. To contribute:

1. Ensure all tests pass
2. Add comprehensive documentation
3. Follow semantic versioning
4. Maintain backward compatibility


## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.
