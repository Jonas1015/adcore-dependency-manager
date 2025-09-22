#!/usr/bin/env python3
"""
Command-line interface for the Dependency Manager.

Provides pip-like commands for dependency management with intelligent caching.
"""

import argparse
import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional

from .dependency_manager import DependencyManager


def setup_logging(verbose: bool = False):
    """Set up logging for CLI usage."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def cmd_install(args):
    """Install packages with dependency resolution."""
    setup_logging(args.verbose)

    dm = DependencyManager(cache_dir=args.cache_dir)

    if args.requirements:
        # Install from requirements file
        print(f"Installing from {args.requirements}...")
        requirements = {args.requirements: Path(args.requirements).read_text()}
        asyncio.run(dm.resolve_dependencies(requirements))
    elif args.packages:
        # Install specific packages
        print(f"Installing packages: {', '.join(args.packages)}...")
        requirements = {"cli": "\n".join(args.packages)}
        asyncio.run(dm.resolve_dependencies(requirements))
    else:
        # Auto-discover and install
        print("Auto-discovering and installing requirements...")
        asyncio.run(dm.resolve_dependencies())

    print("✅ Installation completed")


def cmd_resolve(args):
    """Resolve dependencies without installing."""
    setup_logging(args.verbose)

    dm = DependencyManager(cache_dir=args.cache_dir)

    if args.requirements:
        requirements = {args.requirements: Path(args.requirements).read_text()}
    else:
        requirements = None

    print("Resolving dependencies...")
    asyncio.run(dm.resolve_dependencies(
        modules_requirements=requirements,
        requirements_file_pattern=args.pattern,
        search_dirs=args.search_dirs
    ))

    print("✅ Dependencies resolved")


def cmd_cache(args):
    """Manage dependency cache."""
    setup_logging(args.verbose)

    dm = DependencyManager(cache_dir=args.cache_dir)

    if args.clear:
        if args.module:
            dm.invalidate_module_cache(args.module)
            print(f"✅ Cleared cache for module: {args.module}")
        else:
            dm.invalidate_cache()
            print("✅ Cleared entire dependency cache")
    elif args.info:
        cache = dm.load_cache()
        print(f"Cache directory: {dm.cache_dir}")
        print(f"Combined hash: {cache.get('combined_hash', 'None')}")
        print(f"Last updated: {cache.get('last_updated', 'Never')}")
        print(f"Resolved packages: {len(cache.get('resolved_packages', {}))}")
        print(f"Module caches: {len(cache.get('requirements_caches', {}))}")


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Intelligent dependency management with caching",
        prog="dependency-manager"
    )

    parser.add_argument(
        "--cache-dir",
        default=".dependency_cache",
        help="Cache directory (default: .dependency_cache)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser(
        "install",
        help="Install packages with dependency resolution"
    )
    install_parser.add_argument(
        "packages",
        nargs="*",
        help="Packages to install"
    )
    install_parser.add_argument(
        "-r", "--requirements",
        help="Install from requirements file"
    )
    install_parser.set_defaults(func=cmd_install)

    # Resolve command
    resolve_parser = subparsers.add_parser(
        "resolve",
        help="Resolve dependencies without installing"
    )
    resolve_parser.add_argument(
        "-r", "--requirements",
        help="Requirements file to resolve"
    )
    resolve_parser.add_argument(
        "-p", "--pattern",
        default="requirements.txt",
        help="File pattern to search for (default: requirements.txt)"
    )
    resolve_parser.add_argument(
        "--search-dirs",
        nargs="*",
        help="Directories to search for requirements files"
    )
    resolve_parser.set_defaults(func=cmd_resolve)

    # Cache command
    cache_parser = subparsers.add_parser(
        "cache",
        help="Manage dependency cache"
    )
    cache_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear cache"
    )
    cache_parser.add_argument(
        "--module",
        help="Clear cache for specific module (use with --clear)"
    )
    cache_parser.add_argument(
        "--info",
        action="store_true",
        help="Show cache information"
    )
    cache_parser.set_defaults(func=cmd_cache)

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        args.func(args)
        return 0
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())