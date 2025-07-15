import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from trello_cli.main import app

runner = CliRunner()

@patch('trello_cli.main.SessionLocal')
def test_config_trello_command(MockSessionLocal):
    # Mock the session instance
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Configure the mock to return the mock_session
    MockSessionLocal.return_value = mock_session

    result = runner.invoke(
        app,
        ["config", "trello"],
        input="test_api_key\ntest_api_secret\ntest_token\n",
    )

    print(result.stdout)
    assert result.exit_code == 0
    assert "Trello configuration saved successfully." in result.stdout
    assert mock_session.add.call_count == 3
    mock_session.commit.assert_called_once()
