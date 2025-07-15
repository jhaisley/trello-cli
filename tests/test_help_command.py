from typer.testing import CliRunner
from trello_cli.main import app

runner = CliRunner()

def test_help_command():
    """
    Tests that the help command runs successfully and contains expected output for
    the main command and subcommands.
    """
    result = runner.invoke(app, ["help"], prog_name="trello-cli")
    assert result.exit_code == 0
    
    # Check for main help output
    assert "Usage: trello-cli [OPTIONS] COMMAND [ARGS]..." in result.stdout
    
    # Check for subcommand help sections
    assert "labels" in result.stdout
    assert "config" in result.stdout
    assert "boards" in result.stdout
    assert "cards" in result.stdout