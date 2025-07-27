# Trello Tools

[![Python Version](https://img.shields.io/pypi/pyversions/trello-tools.svg)](https://pypi.org/project/trello-tools)
[![PyPI Version](https://img.shields.io/pypi/v/trello-tools.svg)](https://pypi.org/project/trello-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/trello-tools.svg)](https://pypi.org/project/trello-tools)

A powerful command-line interface (CLI) for interacting with Trello. Manage your boards, lists, cards, and labels without leaving the terminal.

## 🚀 Quick Start

### Option 1: Install from PyPI (Recommended)

```bash
pip install trello-tools
trello-tools --help
```

### Option 2: Download Standalone Executable

No Python required! Download the latest `trello-tools.exe` from [GitHub Releases](https://github.com/jhaisley/trello-tools/releases).

### Option 3: Install from Source

```bash
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools
pip install -e .
```

## Table of Contents

- [Trello Tools](#trello-tools)
  - [Description](#description)
  - [History](#history)
  - [Features](#features)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Trello API](#trello-api)
    - [Gemini API (for AI labeling)](#gemini-api-for-ai-labeling)
    - [Set a Default Board](#set-a-default-board)
  - [Usage](#usage)
    - [General Help](#general-help)
    - [Board Commands](#board-commands)
    - [Card Commands](#card-commands)
    - [Label Commands](#label-commands)
    - [Automated Tasks](#automated-tasks)
  - [Development](#development)
  - [Testing](#testing)
  - [Contributing](#contributing)
  - [License](#license)
  - [Disclaimer](#disclaimer)

## Description

This CLI provides a comprehensive set of commands to manage your Trello boards. It's built with Python, Typer, and the `py-trello` library. It also includes a feature to automatically label cards using the Gemini API.

## History

This project started as a single-purpose utility called `tlabeler` to automatically label unlabeled Trello cards using AI. This helped with personal organization and sorting. After others saw its usefulness and wanted to use it, the project expanded to include more general-purpose commands for manual use and scripting.

The CLI has since been used for various purposes, including:

- Managing technical support tickets
- Tracking outages
- Creating boards for new clients and projects
- CI/CD remediation and integration

Given its wide range of uses, the project has been made public to be used by a wider audience.

## Features

### 📋 **Board Management**

- **View all boards**: List all your Trello boards with IDs
- **Create new boards**: Set up new projects instantly
- **List management**: View all lists on any board
- **Board reporting**: Generate activity reports

### 🃏 **Card Operations**

- **Create cards**: Add new cards to any list
- **Move cards**: Transfer cards between lists seamlessly
- **Comment system**: Add comments to cards for collaboration
- **Bulk operations**: Process multiple cards efficiently

### 🏷️ **Smart Labeling**

- **Manual labeling**: Apply labels to unlabeled cards in bulk
- **AI-powered labeling**: Automatically categorize cards using Google Gemini AI
- **Label management**: Create, delete, and organize labels
- **Intelligent suggestions**: Get context-aware label recommendations

### 🤖 **AI Features**

- **Google Gemini integration**: Leverage AI for intelligent card processing
- **Automatic categorization**: Smart labeling based on card content
- **Context understanding**: AI analyzes card titles and descriptions
- **Batch processing**: Handle multiple cards with AI assistance

### ⚙️ **Configuration & Setup**

- **Easy API setup**: Simple configuration for Trello and Gemini APIs
- **Default boards**: Set frequently-used boards as defaults
- **Secure storage**: API keys stored securely in local database
- **Environment support**: Load configuration from `.env` files

### 🔧 **Advanced Tools**

- **Automated archiving**: Archive inactive cards based on age
- **Export functionality**: Backup boards to Loomic format
- **Database management**: Local SQLite database for settings
- **Comprehensive help**: Built-in help system for all commands

### 💻 **Multiple Distribution Options**

- **PyPI package**: `pip install trello-tools`
- **Standalone executable**: No Python required (~40MB)
- **Source installation**: Full development setup
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### 📦 From PyPI (Recommended)

```bash
pip install trello-tools
trello-tools --help
```

### ⚡ Standalone Executable (No Python Required)

Download the latest `trello-tools.exe` (~40MB) from [GitHub Releases](https://github.com/jhaisley/trello-tools/releases):

1. Go to [Releases](https://github.com/jhaisley/trello-tools/releases)
2. Download `trello-tools.exe` from the latest release
3. Run it directly: `trello-tools.exe --help`

Perfect for users who don't have Python installed!

### 🔧 From Source (Development)

```bash
# Clone the repository
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools

# Install with uv (recommended for development)
uv sync
uv run trello-tools --help

# Or install with pip
pip install -e .
trello-tools --help
```

## Configuration

Before you can use the Trello CLI, you need to configure your Trello API credentials and, optionally, your Gemini API key.

### Trello API

1. **Get your API Key and Token**:
    - Go to [https://trello.com/app-key](https://trello.com/app-key) to get your API key.
    - From that page, you can also generate a token.

2. **Set your credentials**:
    You can set your credentials in two ways:

    - **Using the `config trello` command**:

        ```bash
        trello-tools config trello
        ```

        You will be prompted to enter your API key, API secret, and token.

    - **Using a `.env` file**:
        Create a `.env` file in your home directory (`~/.env`) with the following content:

        ```text
        TRELLO_API_KEY="your_api_key"
        TRELLO_API_SECRET="your_api_secret"
        TRELLO_TOKEN="your_token"
        ```

        Then, load the configuration:

        ```bash
        trello-tools config load
        ```

### Gemini API (for AI labeling)

1. **Get your API Key**:
    - Go to [https://makersuite.google.com/](https://makersuite.google.com/) to get your Gemini API key.

2. **Set your API key**:

    ```bash
    trello-tools config gemini
    ```

    You will be prompted to enter your API key.

### Set a Default Board

You can set a default board to avoid having to specify the board ID for every command.

1. **Find your board ID**:
    You can find your board ID by running:

    ```bash
    trello-tools boards show
    ```

    The board ID is the long string of characters after the board name.

2. **Set the default board**:

    ```bash
    trello-tools config set-default-board "your_board_id"
    ```

## Usage

The Trello CLI is organized into several subcommands.

### General Help

You can get help for any command or subcommand by using the `--help` flag.

```bash
trello-tools --help
trello-tools boards --help
trello-tools cards --help
```

### Board Commands

- **Show all boards**:

    ```bash
    trello-tools boards show
    ```

- **Create a new board**:

    ```bash
    trello-tools boards create "My New Board"
    ```

- **List all lists on a board**:

    ```bash
    trello-tools boards lists --board-id "your_board_id"
    ```

### Card Commands

- **Create a new card**:

    ```bash
    trello-tools cards create "your_list_id" "My New Card"
    ```

- **Move a card to another list**:

    ```bash
    trello-tools cards move "your_card_id" "your_new_list_id"
    ```

- **Add a comment to a card**:

    ```bash
    trello-tools cards comment "your_card_id" "This is a comment."
    ```

### Label Commands

- **List all labels on a board**:

    ```bash
    trello-tools labels list --board-id "your_board_id"
    ```

- **Create a new label**:

    ```bash
    trello-tools labels create "My New Label" "blue" --board-id "your_board_id"
    ```

### Automated Tasks

- **Apply a label to all unlabeled cards**:

    ```bash
    trello-tools label "My Label" --board-id "your_board_id"
    ```

- **Automatically label cards using AI**:

    ```bash
    trello-tools ai-label --board-id "your_board_id"
    ```

- **Archive inactive cards**:

    ```bash
    trello-tools archive --days 30 --board-id "your_board_id"
    ```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .[dev]
```

### Development Tools

- **Testing**: `uv run pytest` or `pytest`
- **Linting**: `uv run ruff check .`
- **Formatting**: `uv run ruff format .`
- **Type checking**: Built into ruff
- **Security scanning**: `uv run bandit -r src/`

### Building and Releasing

```bash
# Build packages
uv build

# Build standalone executable
python build_executable.py

# Version management
uv run bump2version patch  # or minor, major

# Full release process
python version_manager.py patch --release
```

### Project Structure

```text
trello-tools/
├── src/trello_cli/         # Main package code
├── tests/                  # Test suite
├── dist/                   # Built packages and executables
├── build_executable.py     # Executable building script
├── version_manager.py      # Version and release management
├── VERSION_MANAGEMENT.md   # Version management guide
└── pyproject.toml          # Project configuration
```

See [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) for detailed development workflows.

## Testing

To run the tests, you will need to install the development dependencies and then run `pytest`:

```bash
pip install -e .[dev]
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with, endorsed by, or in any way officially connected with Trello, Inc. or any of its subsidiaries or its affiliates. The official Trello website can be found at [https://trello.com](https://trello.com).
