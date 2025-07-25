from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from trello_cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_trello_client_for_labels():
    # Mock Label
    mock_label1 = MagicMock()
    mock_label1.id = "label1_id"
    mock_label1.name = "Label 1"
    mock_label1.color = "blue"

    mock_label2 = MagicMock()
    mock_label2.id = "label2_id"
    mock_label2.name = "Label 2"
    mock_label2.color = "green"

    # Mock Board
    mock_board = MagicMock()
    mock_board.name = "Test Board"
    mock_board.get_labels.return_value = [mock_label1, mock_label2]
    mock_new_label = MagicMock()
    mock_new_label.id = "new_label_id"
    mock_new_label.name = "New Label"
    mock_new_label.color = "red"
    mock_board.add_label.return_value = mock_new_label

    # Mock Client
    mock_client = MagicMock()
    mock_client.get_board.return_value = mock_board

    return mock_client


def test_labels_list_command(mock_trello_client_for_labels):
    with patch(
        "trello_cli.main.get_trello_client", return_value=mock_trello_client_for_labels
    ):
        result = runner.invoke(
            app,
            ["labels", "list", "--board-id", "some_board_id"],
        )

        print(result.stdout)
        assert result.exit_code == 0
        assert "Labels for board 'Test Board':" in result.stdout
        assert "ID: label1_id, Name: Label 1, Color: blue" in result.stdout
        assert "ID: label2_id, Name: Label 2, Color: green" in result.stdout


def test_labels_create_command(mock_trello_client_for_labels):
    with patch(
        "trello_cli.main.get_trello_client", return_value=mock_trello_client_for_labels
    ):
        result = runner.invoke(
            app,
            ["labels", "create", "New Label", "red", "--board-id", "some_board_id"],
        )

        print(result.stdout)
        assert result.exit_code == 0
        assert (
            "Successfully created label 'New Label' with ID 'new_label_id' and color 'red'."
            in result.stdout
        )
        mock_trello_client_for_labels.get_board.return_value.add_label.assert_called_once_with(
            "New Label", "red"
        )


def test_labels_delete_command(mock_trello_client_for_labels):
    with patch(
        "trello_cli.main.get_trello_client", return_value=mock_trello_client_for_labels
    ):
        result = runner.invoke(
            app,
            ["labels", "delete", "some_label_id", "--board-id", "some_board_id"],
        )

        print(result.stdout)
        assert result.exit_code == 0
        assert "Deleting labels is not currently supported" in result.stdout
