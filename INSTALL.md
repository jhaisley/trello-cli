# Installation Guide

Trello Tools offers multiple installation methods to suit different users and environments.

## 🚀 Quick Installation

### For Most Users: PyPI Installation

```bash
pip install trello-tools
trello-tools --help
```

### For Non-Python Users: Standalone Executable

1. **Download**: Go to [GitHub Releases](https://github.com/jhaisley/trello-tools/releases)
2. **Get the executable**: Download `trello-tools.exe` (~40MB)
3. **Run**: Double-click or use in terminal: `trello-tools.exe --help`

✅ **No Python installation required!**

## 📋 Detailed Installation Options

### 1. PyPI Installation (Recommended)

**Requirements**: Python 3.11+

```bash
# Install trello-tools
pip install trello-tools

# Verify installation
trello-tools --version
trello-tools --help
```

**Upgrade to latest version:**

```bash
pip install --upgrade trello-tools
```

### 2. Standalone Executable

**Requirements**: None (self-contained)

**Windows:**

1. Visit [GitHub Releases](https://github.com/jhaisley/trello-tools/releases)
2. Download `trello-tools.exe` from the latest release
3. Place it in a folder in your PATH (optional)
4. Run: `trello-tools.exe --help`

**Benefits:**

- No Python installation needed
- Portable - runs anywhere
- Perfect for corporate environments
- Single file distribution

### 3. Development Installation

**Requirements**: Python 3.11+, Git

#### Using uv (Recommended for developers)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools

# Install in development mode
uv sync

# Run from source
uv run trello-tools --help
```

#### Using pip

```bash
# Clone repository
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools

# Install in development mode
pip install -e .

# Run
trello-tools --help
```

### 4. Virtual Environment Installation

**Recommended for isolated installations:**

```bash
# Create virtual environment
python -m venv trello-tools-env

# Activate (Windows)
trello-tools-env\Scripts\activate

# Activate (macOS/Linux)
source trello-tools-env/bin/activate

# Install
pip install trello-tools

# Use
trello-tools --help
```

## 🔧 Post-Installation Setup

After installation, configure your Trello API credentials:

```bash
# Set up Trello API access
trello-tools config trello

# Optional: Set up AI features
trello-tools config gemini

# Optional: Set default board
trello-tools config set-default-board "your_board_id"
```

## ✅ Verify Installation

Test your installation:

```bash
# Check version
trello-tools --version

# See available commands
trello-tools --help

# List your boards (requires API setup)
trello-tools boards show
```

## 🔧 Troubleshooting

### Python not found

- **Solution**: Install Python 3.11+ from [python.org](https://python.org)
- **Alternative**: Use the standalone executable

### Permission errors

- **Windows**: Run terminal as Administrator
- **macOS/Linux**: Use `sudo pip install trello-tools`
- **Better solution**: Use virtual environments

### Package conflicts

- **Solution**: Use a virtual environment
- **Quick fix**: `pip install --user trello-tools`

### Import errors

- **Check Python version**: `python --version` (needs 3.11+)
- **Reinstall**: `pip uninstall trello-tools && pip install trello-tools`

## 📚 Next Steps

1. **Configure APIs**: See [Configuration Guide](README.md#configuration)
2. **Learn commands**: Run `trello-tools help`
3. **View examples**: Check the [README](README.md) for usage examples
4. **Get support**: Open an issue on [GitHub](https://github.com/jhaisley/trello-tools/issues)

## 🔄 Updating

### PyPI Installation

```bash
pip install --upgrade trello-tools
```

### Standalone Executable

Download the latest `trello-tools.exe` from releases and replace your existing file.

### Development Installation

```bash
cd trello-tools
git pull
uv sync  # or pip install -e .
```
