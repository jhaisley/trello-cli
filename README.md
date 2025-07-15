# Trello CLI

[![Python Version](https://img.shields.io/pypi/pyversions/trello-cli.svg)](https://pypi.org/project/trello-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful command-line interface (CLI) for interacting with Trello. Manage your boards, lists, cards, and labels without leaving the terminal.

## Table of Contents

- [Trello CLI](#trello-cli)
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

- **Board Management**: Create, update, close, and view your Trello boards.
- **List Management**: View all lists on a board.
- **Card Management**: Create, update, delete, move, and comment on cards.
- **Label Management**: Create, delete, and view labels on a board.
- **Automated Labeling**:
    - Apply a specific label to all unlabeled cards.
    - Automatically label cards using the Gemini API for intelligent suggestions.
- **Bulk Archiving**: Archive inactive cards based on a specified number of days.
- **Reporting**: Generate a report of board activity.
- **Configuration**: Easily configure your Trello and Gemini API keys.

## Installation

You can install the Trello CLI using pip:

```bash
pip install trello-cli
```

## Configuration

Before you can use the Trello CLI, you need to configure your Trello API credentials and, optionally, your Gemini API key.

### Trello API

1.  **Get your API Key and Token**:
    - Go to [https://trello.com/app-key](https://trello.com/app-key) to get your API key.
    - From that page, you can also generate a token.

2.  **Set your credentials**:
    You can set your credentials in two ways:

    - **Using the `config trello` command**:
        ```bash
        trello-cli config trello
        ```
        You will be prompted to enter your API key, API secret, and token.

    - **Using a `.env` file**:
        Create a `.env` file in your home directory (`~/.env`) with the following content:
        ```
        TRELLO_API_KEY="your_api_key"
        TRELLO_API_SECRET="your_api_secret"
        TRELLO_TOKEN="your_token"
        ```
        Then, load the configuration:
        ```bash
        trello-cli config load
        ```

### Gemini API (for AI labeling)

1.  **Get your API Key**:
    - Go to [https://makersuite.google.com/](https://makersuite.google.com/) to get your Gemini API key.

2.  **Set your API key**:
    ```bash
    trello-cli config gemini
    ```
    You will be prompted to enter your API key.

### Set a Default Board

You can set a default board to avoid having to specify the board ID for every command.

1.  **Find your board ID**:
    You can find your board ID by running:
    ```bash
    trello-cli boards show
    ```
    The board ID is the long string of characters after the board name.

2.  **Set the default board**:
    ```bash
    trello-cli config set-default-board "your_board_id"
    ```

## Usage

The Trello CLI is organized into several subcommands.

### General Help

You can get help for any command or subcommand by using the `--help` flag.

```bash
trello-cli --help
trello-cli boards --help
trello-cli cards --help
```

### Board Commands

- **Show all boards**:
    ```bash
    trello-cli boards show
    ```

- **Create a new board**:
    ```bash
    trello-cli boards create "My New Board"
    ```

- **List all lists on a board**:
    ```bash
    trello-cli boards lists --board-id "your_board_id"
    ```

### Card Commands

- **Create a new card**:
    ```bash
    trello-cli cards create "your_list_id" "My New Card"
    ```

- **Move a card to another list**:
    ```bash
    trello-cli cards move "your_card_id" "your_new_list_id"
    ```

- **Add a comment to a card**:
    ```bash
    trello-cli cards comment "your_card_id" "This is a comment."
    ```

### Label Commands

- **List all labels on a board**:
    ```bash
    trello-cli labels list --board-id "your_board_id"
    ```

- **Create a new label**:
    ```bash
    trello-cli labels create "My New Label" "blue" --board-id "your_board_id"
    ```

### Automated Tasks

- **Apply a label to all unlabeled cards**:
    ```bash
    trello-cli label "My Label" --board-id "your_board_id"
    ```

- **Automatically label cards using AI**:
    ```bash
    trello-cli ai-label --board-id "your_board_id"
    ```

- **Archive inactive cards**:
    ```bash
    trello-cli archive --days 30 --board-id "your_board_id"
    ```

## Development

To set up the development environment, you will need to install the project in editable mode with the development dependencies:

```bash
pip install -e .[dev]
```

This will install the project and the dependencies listed in `pyproject.toml`.

## Testing

To run the tests, you will need to install the development dependencies and then run `pytest`:

```bash
pip install -e .[dev]
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -am 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with, endorsed by, or in any way officially connected with Trello, Inc. or any of its subsidiaries or its affiliates. The official Trello website can be found at [https://trello.com](https://trello.com).
