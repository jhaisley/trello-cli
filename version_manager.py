#!/usr/bin/env python3
"""
Version management script for trello-tools.

This script provides convenient commands for bumping versions and creating releases.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
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


def bump_version(part):
    """Bump version using bump2version."""
    if not run_command(f"uv run bump2version {part}", f"Bumping {part} version"):
        return False

    # Regenerate lock file to update version references
    if not run_command("uv lock", "Regenerating lock file"):
        return False

    # Commit the updated lock file
    if not run_command('git add uv.lock && git commit -m "Update uv.lock after version bump"', "Committing updated lock file"):
        return False

    # Get the new version
    result = subprocess.run(
        "uv run bump2version --dry-run --list patch",
        shell=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.split("\n"):
        if line.startswith("new_version="):
            new_version = line.split("=")[1]
            print(f"🎉 Version bumped to {new_version}")
            return new_version
    return None


def create_release(version):
    """Create GitHub release and build packages."""
    print(f"\n🚀 Creating release for version {version}...")

    # Build packages
    if not run_command("uv build", "Building Python packages"):
        return False

    # Build executable
    if not run_command(
        "python build_executable.py --exe-only", "Building standalone executable"
    ):
        return False

    # Push changes and tags
    if not run_command("git push", "Pushing changes"):
        return False

    if not run_command(f"git push origin v{version}", "Pushing tag"):
        return False

    # Create GitHub release with both packages and executable
    release_cmd = f'gh release create v{version} "dist/trello_tools-{version}.tar.gz" "dist/trello_tools-{version}-py3-none-any.whl" "dist/trello-tools.exe" --title "Trello Tools v{version}" --generate-notes'
    if not run_command(release_cmd, "Creating GitHub release"):
        return False

    print(f"✅ Release v{version} created successfully!")
    print("📦 PyPI upload: uv run twine upload dist/*.tar.gz dist/*.whl")
    return True


def main():
    parser = argparse.ArgumentParser(description="Manage versions for trello-tools")
    parser.add_argument(
        "part", choices=["patch", "minor", "major"], help="Part of version to bump"
    )
    parser.add_argument(
        "--release", action="store_true", help="Create GitHub release after bumping"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    if args.dry_run:
        print(f"🔍 Dry run: Would bump {args.part} version")
        return run_command(
            f"uv run bump2version --dry-run --verbose {args.part}",
            "Dry run version bump",
        )

    # Bump version
    new_version = bump_version(args.part)
    if not new_version:
        return False

    # Create release if requested
    if args.release:
        return create_release(new_version)

    print(f"\n💡 To create a release, run:")
    print(f"   python version_manager.py {args.part} --release")
    print(f"💡 To upload to PyPI, run:")
    print(f"   uv run twine upload dist/*")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
