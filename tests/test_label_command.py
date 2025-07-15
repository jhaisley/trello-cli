import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch
from trello_cli.main import app

runner = CliRunner()

@pytest.fixture
def mock_trello_client():
    # Mock Label
    mock_label = MagicMock()
    mock_label.name = "Test Label"

    # Mock Cards
    mock_card_labeled = MagicMock()
    mock_card_labeled.name = "Labeled Card"
    mock_card_labeled.labels = [mock_label]

    mock_card_unlabeled = MagicMock()
    mock_card_unlabeled.name = "Unlabeled Card"
    mock_card_unlabeled.labels = []
    # We need to mock the add_label method for this card
    mock_card_unlabeled.add_label = MagicMock()

    # Mock Board
    mock_board = MagicMock()
    mock_board.name = "Test Board"
    mock_board.get_labels.return_value = [mock_label]
    mock_board.all_cards.return_value = [mock_card_labeled, mock_card_unlabeled]

    # Mock Client
    mock_client = MagicMock()
    mock_client.get_board.return_value = mock_board
    
    return mock_client, mock_card_unlabeled, mock_label

def test_label_command(mock_trello_client):
    mock_client, mock_card_unlabeled, mock_label_obj = mock_trello_client

    with patch('trello_cli.main.get_trello_client', return_value=mock_client):
        result = runner.invoke(
            app,
            ["label", "some_board_id", "Test Label"],
        )

        print(result.stdout)
        assert result.exit_code == 0
        assert "Found 1 unlabeled cards" in result.stdout
        assert "Applying label 'Test Label'..." in result.stdout
        assert "Applied label to card: 'Unlabeled Card'" in result.stdout
        
        # Verify that add_label was called on the unlabeled card with the correct label
        mock_card_unlabeled.add_label.assert_called_once_with(mock_label_obj)
