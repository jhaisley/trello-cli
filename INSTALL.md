# Installation Guide

## Quick Installation (Recommended)

### From PyPI (when published)

```bash
pip install trello-tools
```

### From Source (Current)
```bash
# Clone the repository
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools

# Install with uv (recommended)
uv sync
uv run trello-tools --help

# Or install with pip
pip install -e .
trello-tools --help
```

## Installation Methods

### 1. Using uv (Recommended for Development)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools
uv sync
```

### 2. Using pip

```bash
# Clone and install
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools
pip install -e .
```

### 3. Standalone Executable (No Python Required)

For users who don't want to install Python:

```bash
# Download from GitHub Releases
# (Or build yourself with: python build_executable.py)
```

## Next Steps

After installation, you'll need to configure your Trello API credentials:

```bash
trello-tools config trello
```

See the [README](README.md) for full configuration and usage instructions.
