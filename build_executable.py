#!/usr/bin/env python3
"""
Build script to create a standalone executable using PyInstaller.
This allows distribution without requiring Python to be installed.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        if isinstance(cmd, list):
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(
                cmd, shell=True, check=True, capture_output=True, text=True
            )

        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Details: {e.stderr}")
        return False


def clean_build_dirs():
    """Clean previous build artifacts (but preserve packages)."""
    # Only clean the build directory and PyInstaller artifacts
    # Keep the packages from uv build
    dirs_to_clean = ["build"]
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_path)

    # Remove only the executable from dist, not the packages
    dist_path = Path("dist")
    if dist_path.exists():
        exe_path = dist_path / "trello-tools.exe"
        if exe_path.exists():
            print("🧹 Removing old executable")
            exe_path.unlink()


def build_executable():
    """Build a standalone executable using PyInstaller."""

    # Clean previous builds
    clean_build_dirs()

    # Create a more comprehensive build command using uv run
    cmd = [
        "uv",
        "run",
        "pyinstaller",
        "--onefile",  # Single executable file
        "--name",
        "trello-tools",  # Executable name
        "--console",  # Console application
        "--clean",  # Clean build cache
        "--noconfirm",  # Overwrite output directory
        "--add-data",
        "src;src",  # Include source code
        "--add-data",
        "README.md;.",  # Include README
        "--hidden-import",
        "pkg_resources.extern",  # Fix potential import issues
        "--hidden-import",
        "trello_cli.database",
        "--hidden-import",
        "trello_cli.models",
        "--hidden-import",
        "trello_cli.trello",
        "trello_tools_main.py",  # Entry point
    ]

    if not run_command(cmd, "Building standalone executable"):
        return False

    # Check if executable was created
    exe_path = Path("dist/trello-tools.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("🎉 Executable built successfully!")
        print(f"📁 Location: {exe_path.absolute()}")
        print(f"📊 Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"❌ Executable not found at {exe_path}")
        return False


def build_packages():
    """Build Python packages using uv."""
    return run_command("uv build", "Building Python packages")


def main():
    """Main build function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build trello-tools executable and packages"
    )
    parser.add_argument("--exe-only", action="store_true", help="Build executable only")
    parser.add_argument(
        "--packages-only", action="store_true", help="Build packages only"
    )

    args = parser.parse_args()

    success = True

    if args.packages_only:
        success = build_packages()
    elif args.exe_only:
        success = build_executable()
    else:
        # Build both by default
        print("🚀 Building trello-tools executable and packages...")
        print()

        # Build packages first
        if not build_packages():
            success = False

        print()

        # Build executable
        if not build_executable():
            success = False

    if success:
        print("\n🎉 Build completed successfully!")
        print("\n📦 Distribution files:")
        dist_path = Path("dist")
        if dist_path.exists():
            for file in sorted(dist_path.iterdir()):
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"   📄 {file.name} ({size_mb:.1f} MB)")
    else:
        print("\n❌ Build failed!")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
