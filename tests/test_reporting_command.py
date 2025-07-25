from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from trello_cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_trello_client_for_reporting():
    now = datetime.now(timezone.utc)

    actions = [
        {
            "type": "createCard",
            "date": (now - timedelta(days=2)).isoformat(),
            "data": {"card": {"name": "New Card 1"}},
        },
        {
            "type": "updateCard",
            "date": (now - timedelta(days=3)).isoformat(),
            "data": {
                "card": {"name": "Moved Card", "closed": False},
                "listBefore": {"name": "To Do"},
                "listAfter": {"name": "In Progress"},
            },
        },
        {
            "type": "updateCard",
            "date": (now - timedelta(days=4)).isoformat(),
            "data": {"card": {"name": "Archived Card", "closed": True}},
        },
        {
            "type": "commentCard",  # Should be ignored
            "date": (now - timedelta(days=1)).isoformat(),
            "data": {"card": {"name": "Commented Card"}},
        },
        {
            "type": "createCard",  # Old action, should be ignored
            "date": (now - timedelta(days=10)).isoformat(),
            "data": {"card": {"name": "Old Card"}},
        },
    ]

    # Mock Board
    mock_board = MagicMock()
    mock_board.name = "Test Board"
    mock_board.fetch_actions.return_value = actions

    # Mock Client
    mock_client = MagicMock()
    mock_client.get_board.return_value = mock_board

    return mock_client


def test_report_command(mock_trello_client_for_reporting):
    with patch(
        "trello_cli.main.get_trello_client",
        return_value=mock_trello_client_for_reporting,
    ):
        result = runner.invoke(
            app,
            ["report", "--board-id", "some_board_id", "--days", "7"],
        )

        print(result.stdout)
        assert result.exit_code == 0
        assert "# Report for board 'Test Board' for the last 7 days" in result.stdout
        assert "## Cards Created" in result.stdout
        assert "- New Card 1" in result.stdout
        assert "## Cards Moved" in result.stdout
        assert "- 'Moved Card' moved from 'To Do' to 'In Progress'" in result.stdout
        assert "## Cards Archived" in result.stdout
        assert "- Archived Card" in result.stdout
        assert "Old Card" not in result.stdout
        assert "Commented Card" not in result.stdout
