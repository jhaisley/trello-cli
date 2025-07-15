from typer.testing import CliRunner
from trello_cli.main import app
from trello_cli.database import SessionLocal
from trello_cli.models import Config
import pytest

runner = CliRunner()

@pytest.fixture(autouse=True)
def clear_db():
    db = SessionLocal()
    db.query(Config).delete()
    db.commit()
    db.close()

def test_set_default_board():
    """
    Tests that the `config set-default-board` command saves the board ID.
    """
    result = runner.invoke(app, ["config", "set-default-board", "my_board_id"])
    assert result.exit_code == 0
    assert "Default board ID set to 'my_board_id'." in result.stdout

    db = SessionLocal()
    board_id = db.query(Config).filter(Config.key == "DEFAULT_BOARD_ID").first()
    db.close()
    assert board_id is not None
    assert board_id.value == "my_board_id"

def test_use_default_board_id():
    """
    Tests that commands use the default board ID when it is set.
    """
    runner.invoke(app, ["config", "set-default-board", "my_board_id"])

    # This will fail because it requires a real board ID, but it will fail
    # after the point where the board ID is retrieved, which is what we want to test.
    result = runner.invoke(app, ["label", "My Label"])
    assert "Error connecting to Trello or finding board" in result.stdout

def test_no_default_board_id():
    """
    Tests that the user is prompted for a board ID when no default is set.
    """
    result = runner.invoke(app, ["label", "My Label"])
    assert "No board ID provided and no default board ID set." in result.stdout
