from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from trello_cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_trello_client_for_archive():
    now = datetime.now(timezone.utc)

    # Mock Cards
    mock_card_active = MagicMock()
    mock_card_active.name = "Active Card"
    mock_card_active.date_last_activity = now - timedelta(days=10)

    mock_card_inactive = MagicMock()
    mock_card_inactive.name = "Inactive Card"
    mock_card_inactive.date_last_activity = now - timedelta(days=40)
    mock_card_inactive.set_closed = MagicMock()

    # Mock Board
    mock_board = MagicMock()
    mock_board.name = "Test Board"
    mock_board.open_cards.return_value = [mock_card_active, mock_card_inactive]

    # Mock Client
    mock_client = MagicMock()
    mock_client.get_board.return_value = mock_board

    return mock_client, mock_card_inactive


def test_archive_command(mock_trello_client_for_archive):
    mock_client, mock_card_inactive = mock_trello_client_for_archive

    with patch("trello_cli.main.get_trello_client", return_value=mock_client):
        result = runner.invoke(
            app,
            ["archive", "--board-id", "some_board_id", "--days", "30"],
        )

        print(result.stdout)
        assert result.exit_code == 0
        assert "Found 2 open cards" in result.stdout
        assert "Checking for inactivity..." in result.stdout
        assert "Archived card: 'Inactive Card'" in result.stdout

        # Verify that set_closed(True) was called on the inactive card
        mock_card_inactive.set_closed.assert_called_once_with(True)


def test_archive_command_no_inactive(mock_trello_client_for_archive):
    mock_client, _ = mock_trello_client_for_archive
    # Modify the mock to return no inactive cards
    active_cards = [
        c
        for c in mock_client.get_board.return_value.open_cards()
        if c.date_last_activity > datetime.now(timezone.utc) - timedelta(days=30)
    ]
    mock_client.get_board.return_value.open_cards.return_value = active_cards

    with patch("trello_cli.main.get_trello_client", return_value=mock_client):
        result = runner.invoke(
            app,
            ["archive", "--board-id", "some_board_id", "--days", "30"],
        )

        print(result.stdout)
        assert result.exit_code == 0
        assert "Found 1 open cards" in result.stdout
        assert "Archiving complete." in result.stdout
        assert "Archived card" not in result.stdout
