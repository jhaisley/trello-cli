# Trello Tools v0.1.0 - Initial Release

🎉 **Welcome to Trello Tools!**

A powerful command-line interface for managing your Trello boards, cards, and labels - now available on PyPI!

## 🚀 Installation

```bash
pip install trello-tools
```

## 💡 Quick Start

```bash
# Configure your Trello API credentials
trello-tools config trello

# See all available commands
trello-tools --help

# List your boards
trello-tools boards show

# Set a default board (optional)
trello-tools config set-default-board "your_board_id"
```

## ✨ Key Features

### 📋 **Board Management**

- View all your Trello boards
- Create new boards
- List all lists on a board

### 🃏 **Card Management**

- Create new cards
- Move cards between lists
- Add comments to cards
- Archive inactive cards automatically

### 🏷️ **Label Management**

- Create and manage labels
- Apply labels to unlabeled cards in bulk
- **AI-Powered Labeling**: Automatically label cards using Google Gemini AI

### ⚙️ **Configuration**

- Easy setup for Trello API credentials
- Optional Gemini API setup for AI features
- Default board configuration for convenience

### 🔧 **Advanced Features**

- Generate board activity reports
- Export boards to Loomic backup format
- Comprehensive help system for all commands

## 🤖 AI-Powered Features

Configure Google Gemini for intelligent card labeling:

```bash
# Set up Gemini API
trello-tools config gemini

# Automatically label unlabeled cards
trello-tools ai-label --board-id "your_board_id"
```

## 📚 Documentation

- **Repository**: <https://github.com/jhaisley/trello-tools>
- **Installation Guide**: See [INSTALL.md](https://github.com/jhaisley/trello-tools/blob/main/INSTALL.md)
- **Full Documentation**: See [README.md](https://github.com/jhaisley/trello-tools/blob/main/README.md)

## 🔄 Migration from trello-cli

If you were using the previous `trello-cli` package, simply:

1. Uninstall the old package: `pip uninstall trello-cli`
2. Install the new package: `pip install trello-tools`
3. Use `trello-tools` instead of `trello-cli` in your commands

Your configuration and data remain compatible!

## 🛠️ Development

```bash
git clone https://github.com/jhaisley/trello-tools.git
cd trello-tools
uv sync
uv run trello-tools --help
```

## 📋 Requirements

- Python 3.11+
- Trello API credentials
- Optional: Google Gemini API key for AI features

## 🙏 Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest features.

## 📄 License

MIT License - see [LICENSE](https://github.com/jhaisley/trello-tools/blob/main/LICENSE) for details.

---

**Happy Trello managing!** 🚀
