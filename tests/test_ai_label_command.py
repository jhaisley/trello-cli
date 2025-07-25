from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from trello_cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_trello_and_gemini():
    # Mock Label
    mock_label = MagicMock()
    mock_label.name = "AI Label"

    # Mock Cards
    mock_card_unlabeled = MagicMock()
    mock_card_unlabeled.name = "Unlabeled Card"
    mock_card_unlabeled.description = "This card needs a label."
    mock_card_unlabeled.labels = []
    mock_card_unlabeled.add_label = MagicMock()

    # Mock Board
    mock_board = MagicMock()
    mock_board.name = "Test Board"
    mock_board.get_labels.return_value = [mock_label]
    mock_board.all_cards.return_value = [mock_card_unlabeled]

    # Mock Trello Client
    mock_trello_client = MagicMock()
    mock_trello_client.get_board.return_value = mock_board

    # Mock Gemini Model
    mock_gemini_model = MagicMock()
    mock_gemini_model.generate_content.return_value.text = "AI Label"

    return mock_trello_client, mock_gemini_model, mock_card_unlabeled, mock_label


@patch("trello_cli.main.get_trello_client")
@patch("google.generativeai.GenerativeModel")
@patch("trello_cli.main.get_db")
def test_ai_label_command(
    mock_get_db, mock_genai_model, mock_get_trello_client, mock_trello_and_gemini
):
    mock_trello_client, mock_gemini_model, mock_card_unlabeled, mock_label_obj = (
        mock_trello_and_gemini
    )

    # Setup mocks for dependencies
    mock_get_trello_client.return_value = mock_trello_client
    mock_genai_model.return_value = mock_gemini_model

    # Mock database query for Gemini API key
    mock_db_session = MagicMock()
    mock_gemini_key = MagicMock()
    mock_gemini_key.value = "test_gemini_key"
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_gemini_key
    )
    # The get_db function is a generator, so we need to handle the context management
    mock_get_db.return_value.__enter__.return_value = mock_db_session

    result = runner.invoke(
        app,
        ["ai-label", "--board-id", "some_board_id"],
    )

    print(result.stdout)
    assert result.exit_code == 0
    assert "Found 1 unlabeled cards. Analyzing..." in result.stdout
    assert "Analyzing card: 'Unlabeled Card'" in result.stdout
    assert "Applied labels: AI Label" in result.stdout

    # Verify that add_label was called on the unlabeled card with the correct label
    mock_card_unlabeled.add_label.assert_called_once_with(mock_label_obj)
    mock_gemini_model.generate_content.assert_called_once()
