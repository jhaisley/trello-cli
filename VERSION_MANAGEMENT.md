# Version Management Guide

This project uses `bump2version` for automated version management. This ensures consistent version updates across all files and creates proper git tags.

## Quick Commands

### Bump Version (Manual)

```bash
# Patch version (0.1.0 → 0.1.1)
uv run bump2version patch

# Minor version (0.1.0 → 0.2.0)  
uv run bump2version minor

# Major version (0.1.0 → 1.0.0)
uv run bump2version major
```

### Using the Version Manager Script

```bash
# Dry run to see what would change
python version_manager.py patch --dry-run

# Bump patch version
python version_manager.py patch

# Bump minor version and create GitHub release
python version_manager.py minor --release
```

## What Happens During Version Bump

1. **Updates version in files**:
   - `pyproject.toml`
   - `src/trello_cli/__init__.py`
   - `.bumpversion.cfg`

2. **Creates git commit** with message: `Bump version: X.Y.Z → X.Y.Z+1`

3. **Creates git tag** with name: `vX.Y.Z`

## Building Executables

### Standalone Executable

Build a standalone executable that doesn't require Python:

```bash
# Build executable only
python build_executable.py --exe-only

# Build packages only  
python build_executable.py --packages-only

# Build both (default)
python build_executable.py
```

The executable will be created at `dist/trello-tools.exe` (~40MB) and can be distributed to users who don't have Python installed.

## Release Workflow

### Manual Release

```bash
# 1. Bump version
uv run bump2version patch

# 2. Build packages and executable
uv build
python build_executable.py --exe-only

# 3. Push changes and tags
git push
git push origin v0.1.3  # replace with actual version

# 4. Create GitHub release (with executable)
gh release create v0.1.3 "dist/trello_tools-0.1.3.tar.gz" "dist/trello_tools-0.1.3-py3-none-any.whl" "dist/trello-tools.exe" --title "Trello Tools v0.1.3" --generate-notes

# 5. Upload to PyPI (packages only)
uv run twine upload dist/*.tar.gz dist/*.whl
```

### Automated Release

```bash
# One command to bump, build, and release
python version_manager.py patch --release
```

## Configuration

The version management is configured in `.bumpversion.cfg`:

- **current_version**: Current version number
- **commit**: Auto-commit changes (True)
- **tag**: Auto-create git tag (True)
- **tag_name**: Tag format (`v{new_version}`)
- **Files to update**: Listed in `[bumpversion:file:...]` sections

## Best Practices

1. **Always commit changes** before bumping version
2. **Use semantic versioning**:
   - **Patch** (0.1.0 → 0.1.1): Bug fixes
   - **Minor** (0.1.0 → 0.2.0): New features (backward compatible)
   - **Major** (0.1.0 → 1.0.0): Breaking changes

3. **Test before releasing**:

   ```bash
   # Run tests
   uv run pytest
   
   # Check package builds
   uv build
   ```

4. **Review changes**:

   ```bash
   # Dry run to preview changes
   uv run bump2version --dry-run --verbose patch
   ```

## Troubleshooting

### Working directory not clean

```bash
# Commit your changes first
git add .
git commit -m "Your changes"

# Then bump version
uv run bump2version patch
```

### Version already exists

If you need to re-create a version:

```bash
# Delete tag locally and remotely
git tag -d v0.1.1
git push origin :refs/tags/v0.1.1

# Delete GitHub release
gh release delete v0.1.1

# Then bump again
uv run bump2version patch
```
