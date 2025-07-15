import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch
from trello_cli.main import app

runner = CliRunner()

@pytest.fixture
def mock_trello_client_for_cards():
    # Mock Label
    mock_label = MagicMock()
    mock_label.id = "label_id"
    mock_label.name = "Test Label"

    # Mock Card
    mock_card = MagicMock()
    mock_card.id = "card_id"
    mock_card.name = "Test Card"
    mock_card.description = "A test card."
    mock_card.url = "http://test.com/card"
    mock_card.list_id = "list_id"
    mock_card.board_id = "board_id"
    mock_card.delete.return_value = None
    mock_card.change_list.return_value = None
    mock_card.comment.return_value = None
    mock_card.add_label.return_value = None
    mock_card.remove_label.return_value = None

    # Mock List
    mock_list = MagicMock()
    mock_list.add_card.return_value = mock_card

    # Mock Client
    mock_client = MagicMock()
    mock_client.get_card.return_value = mock_card
    mock_client.get_list.return_value = mock_list
    mock_client.get_label.return_value = mock_label
    
    return mock_client

@patch('trello_cli.main.get_trello_client')
def test_cards_get(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "get", "some_id"])
    assert result.exit_code == 0
    assert "Card Name: Test Card" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_cards_create(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "create", "some_list_id", "New Card"])
    assert result.exit_code == 0
    assert "Successfully created card 'Test Card' with ID 'card_id'." in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_cards_update(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "update", "some_id", "--name", "New Name"])
    assert result.exit_code == 0
    assert "Successfully updated card" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_cards_delete(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "delete", "some_id"])
    assert result.exit_code == 0
    assert "Successfully deleted card 'Test Card'" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_cards_move(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "move", "some_id", "new_list_id"])
    assert result.exit_code == 0
    assert "Successfully moved card 'Test Card' to list 'new_list_id'" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_cards_comment(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "comment", "some_id", "My comment"])
    assert result.exit_code == 0
    assert "Successfully added comment to card 'Test Card'" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_cards_add_label(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "add-label", "some_id", "label_id"])
    assert result.exit_code == 0
    assert "Successfully added label 'Test Label' to card 'Test Card'" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_cards_remove_label(mock_get_trello_client, mock_trello_client_for_cards):
    mock_get_trello_client.return_value = mock_trello_client_for_cards
    result = runner.invoke(app, ["cards", "remove-label", "some_id", "label_id"])
    assert result.exit_code == 0
    assert "Successfully removed label 'Test Label' from card 'Test Card'" in result.stdout
