import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, mock_open
from trello_cli.main import app
from pathlib import Path

runner = CliRunner()

@patch('trello_cli.main.SessionLocal')
@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='export TRELLO_API_KEY="test_key"\nTRELLO_API_SECRET=test_secret\nGEMINI_API_KEY=gemini_key')
def test_config_load_command(mock_file, mock_exists, MockSessionLocal):
    mock_exists.return_value = True
    
    # Mock the session instance
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Configure the mock to return the mock_session
    MockSessionLocal.return_value = mock_session

    result = runner.invoke(
        app,
        ["config", "load", "--path", "/fake/path/.env"],
    )

    assert result.exit_code == 0
    assert "Configuration loaded successfully." in result.stdout
    assert mock_session.add.call_count == 3
    mock_session.commit.assert_called_once()
