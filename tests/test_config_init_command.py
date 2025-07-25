from unittest.mock import patch

from typer.testing import CliRunner

from trello_cli.main import app

runner = CliRunner()


def test_config_init_command_new_database():
    """Test config init when no database exists."""
    with (
        patch("os.path.exists", return_value=False),
        patch("trello_cli.models.Base") as mock_base,
        patch("trello_cli.database.engine") as mock_engine,
    ):
        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0
        assert "Creating empty database..." in result.stdout
        assert "Empty database initialized successfully" in result.stdout
        mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)


def test_config_init_command_existing_database_no_force():
    """Test config init when database exists and no force flag."""
    with patch("os.path.exists", return_value=True):
        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 1
        assert "Database already exists" in result.stdout
        assert "Use --force flag" in result.stdout


def test_config_init_command_existing_database_with_force():
    """Test config init when database exists and force flag is used."""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.remove") as mock_remove,
        patch("trello_cli.models.Base") as mock_base,
        patch("trello_cli.database.engine") as mock_engine,
    ):
        result = runner.invoke(app, ["config", "init", "--force"])

        assert result.exit_code == 0
        assert "Removing existing database" in result.stdout
        assert "Creating empty database..." in result.stdout
        assert "Empty database initialized successfully" in result.stdout
        mock_remove.assert_called_once()
        mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)
