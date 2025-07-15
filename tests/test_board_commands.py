import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch
from trello_cli.main import app

runner = CliRunner()

@pytest.fixture
def mock_trello_client_for_boards():
    # Mock Board
    mock_board = MagicMock()
    mock_board.id = "board_id"
    mock_board.name = "Test Board"
    mock_board.description = "A test board."
    mock_board.url = "http://test.com/board"
    mock_board.close.return_value = None
    mock_list = MagicMock()
    mock_list.name = "To Do"
    mock_list.id = "list1"
    mock_board.all_lists.return_value = [mock_list]

    mock_label = MagicMock()
    mock_label.name = "Bug"
    mock_label.id = "label1"
    mock_label.color = "red"
    mock_board.get_labels.return_value = [mock_label]

    mock_card = MagicMock()
    mock_card.name = "Test Card"
    mock_card.id = "card1"
    mock_board.all_cards.return_value = [mock_card]
    mock_board.get_members.return_value = [MagicMock(full_name="Test User", username="testuser")]
    mock_board.get_powerups.return_value = [{'name': 'Calendar', 'id': 'powerup1'}]

    # Mock Client
    mock_client = MagicMock()
    mock_client.get_board.return_value = mock_board
    mock_client.add_board.return_value = mock_board
    
    return mock_client

@patch('trello_cli.main.get_trello_client')
def test_boards_show(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    mock_trello_client_for_boards.list_boards.return_value = [mock_trello_client_for_boards.get_board("some_id")]
    result = runner.invoke(app, ["boards", "show"])
    assert result.exit_code == 0
    assert "Board Name: Test Board, ID: board_id" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_create(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "create", "New Board"])
    assert result.exit_code == 0
    assert "Successfully created board 'Test Board' with ID 'board_id'." in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_update(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "update", "some_id", "--name", "New Name"])
    assert result.exit_code == 0
    assert "Successfully updated board" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_close(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "close", "some_id"])
    assert result.exit_code == 0
    assert "Successfully closed board 'Test Board'" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_lists(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "lists", "some_id"])
    assert result.exit_code == 0
    assert "Lists on board 'Test Board':" in result.stdout
    assert "- To Do (ID: list1)" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_labels(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "labels", "some_id"])
    assert result.exit_code == 0
    assert "Labels on board 'Test Board':" in result.stdout
    assert "- Bug (ID: label1, Color: red)" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_cards(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "cards", "some_id"])
    assert result.exit_code == 0
    assert "Cards on board 'Test Board':" in result.stdout
    assert "- Test Card (ID: card1)" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_members(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "members", "some_id"])
    assert result.exit_code == 0
    assert "Members of board 'Test Board':" in result.stdout
    assert "- Test User (Username: testuser)" in result.stdout

@patch('trello_cli.main.get_trello_client')
def test_boards_powerups(mock_get_trello_client, mock_trello_client_for_boards):
    mock_get_trello_client.return_value = mock_trello_client_for_boards
    result = runner.invoke(app, ["boards", "powerups", "some_id"])
    assert result.exit_code == 0
    assert "Enabled Power-Ups on board 'Test Board':" in result.stdout
    assert "- Calendar (ID: powerup1)" in result.stdout
