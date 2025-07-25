import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import google.generativeai as genai
import typer
from rich.console import Console
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Config
from .trello import get_trello_client

app = typer.Typer()
labels_app = typer.Typer()
config_app = typer.Typer()
boards_app = typer.Typer()
cards_app = typer.Typer()
app.add_typer(labels_app, name="labels")
app.add_typer(config_app, name="config")
app.add_typer(boards_app, name="boards")
app.add_typer(cards_app, name="cards")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_config(db: Session, key: str, value: str):
    config_item = db.query(Config).filter(Config.key == key).first()
    if config_item:
        config_item.value = value
    else:
        config_item = Config(key=key, value=value)
        db.add(config_item)


@config_app.command("init")
def config_init(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove existing database before creating a new one.",
    ),
):
    """
    Initialize an empty database. Use --force to remove existing database.
    """
    from .database import DATABASE_URL, engine
    from .models import Base

    db_path = DATABASE_URL.replace("sqlite:///", "")

    # Check if database exists
    if os.path.exists(db_path):
        if force:
            print(f"Removing existing database: {db_path}")
            os.remove(db_path)
        else:
            print(f"Database already exists at {db_path}")
            print("Use --force flag to remove existing database and create a new one.")
            raise typer.Exit(code=1)

    # Create all tables
    print("Creating empty database...")
    Base.metadata.create_all(bind=engine)

    print(f"Empty database initialized successfully at: {db_path}")


@config_app.command("load")
def config_load(path: Path = typer.Option("~/.env", help="Path to the .env file.")):
    """
    Load configuration from a .env file.
    """
    env_path = path.expanduser()
    if not env_path.exists():
        print(f"Error: Environment file not found at {env_path}")
        raise typer.Exit(code=1)

    db: Session = next(get_db())

    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("export "):
                line = line[len("export ") :]

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")

            if key in [
                "TRELLO_API_KEY",
                "TRELLO_API_SECRET",
                "TRELLO_TOKEN",
                "GEMINI_API_KEY",
            ]:
                save_config(db, key, value)

    db.commit()
    print("Configuration loaded successfully.")


@config_app.command("trello")
def config_trello(
    api_key: str = typer.Option(..., prompt=True),
    api_secret: str = typer.Option(..., prompt=True),
    token: str = typer.Option(..., prompt=True),
):
    """
    Set Trello API credentials.
    """
    db: Session = next(get_db())

    # In a real app, you'd encrypt these values
    for key, value in [
        ("TRELLO_API_KEY", api_key),
        ("TRELLO_API_SECRET", api_secret),
        ("TRELLO_TOKEN", token),
    ]:
        config_item = db.query(Config).filter(Config.key == key).first()
        if config_item:
            config_item.value = value
        else:
            config_item = Config(key=key, value=value)
            db.add(config_item)

    db.commit()
    print("Trello configuration saved successfully.")


@config_app.command("gemini")
def config_gemini(
    api_key: str = typer.Option(..., prompt=True),
):
    """
    Set Gemini API key.
    """
    db: Session = next(get_db())

    config_item = db.query(Config).filter(Config.key == "GEMINI_API_KEY").first()
    if config_item:
        config_item.value = api_key
    else:
        config_item = Config(key="GEMINI_API_KEY", value=api_key)
        db.add(config_item)

    db.commit()
    print("Gemini API key saved successfully.")


@config_app.command("set-default-board")
def set_default_board(
    board_id: str = typer.Argument(..., help="The ID of the board to set as default."),
):
    """
    Set the default Trello board ID.
    """
    db: Session = next(get_db())
    save_config(db, "DEFAULT_BOARD_ID", board_id)
    db.commit()
    print(f"Default board ID set to '{board_id}'.")


def get_board_id(db: Session, board_id: str = None) -> str:
    if board_id:
        return board_id

    default_board_id = db.query(Config).filter(Config.key == "DEFAULT_BOARD_ID").first()
    if default_board_id:
        return default_board_id.value

    raise typer.BadParameter(
        "No board ID provided and no default board ID set. Please provide a board ID or set a default using 'trello-cli config set-default-board'."
    )


@app.command()
def label(
    label_name: str = typer.Argument(..., help="The name of the label to apply."),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Apply a label to all unlabeled cards on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
    except Exception as e:
        print(f"Error connecting to Trello or finding board: {e}")
        raise typer.Exit(code=1)

    available_labels = {label.name: label for label in board.get_labels()}

    if label_name not in available_labels:
        print(f"Error: Label '{label_name}' not found on board '{board.name}'.")
        print("Available labels are: " + ", ".join(available_labels.keys()))
        raise typer.Exit(code=1)

    label_to_apply = available_labels[label_name]

    unlabeled_cards = [card for card in board.all_cards() if not card.labels]

    if not unlabeled_cards:
        print("No unlabeled cards found.")
        raise typer.Exit()

    print(
        f"Found {len(unlabeled_cards)} unlabeled cards. Applying label '{label_name}'..."
    )

    for card in unlabeled_cards:
        try:
            card.add_label(label_to_apply)
            print(f"  Applied label to card: '{card.name}'")
        except Exception as e:
            print(f"  Failed to apply label to card '{card.name}': {e}")

    print("Labeling complete.")


@app.command()
def archive(
    days: int = typer.Option(
        30, help="The number of days of inactivity to archive cards."
    ),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Archive inactive cards on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
    except Exception as e:
        print(f"Error connecting to Trello or finding board: {e}")
        raise typer.Exit(code=1)

    now = datetime.now(timezone.utc)
    inactive_threshold = now - timedelta(days=days)

    open_cards = board.open_cards()

    if not open_cards:
        print("No open cards found on the board.")
        raise typer.Exit()

    print(f"Found {len(open_cards)} open cards. Checking for inactivity...")

    for card in open_cards:
        if card.date_last_activity < inactive_threshold:
            try:
                card.set_closed(True)
                print(
                    f"  Archived card: '{card.name}' (last activity: {card.date_last_activity})"
                )
            except Exception as e:
                print(f"  Failed to archive card '{card.name}': {e}")

    print("Archiving complete.")


@labels_app.command("list")
def labels_list(
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    List all labels on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
    except Exception as e:
        print(f"Error connecting to Trello or finding board: {e}")
        raise typer.Exit(code=1)

    labels = board.get_labels()
    if not labels:
        print("No labels found on this board.")
        raise typer.Exit()

    print(f"Labels for board '{board.name}':")
    for label in labels:
        print(f"- ID: {label.id}, Name: {label.name}, Color: {label.color}")


@labels_app.command("create")
def labels_create(
    name: str = typer.Argument(..., help="The name of the new label."),
    color: str = typer.Argument(..., help="The color of the new label."),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Create a new label on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        new_label = board.add_label(name, color)
        print(
            f"Successfully created label '{new_label.name}' with ID '{new_label.id}' and color '{new_label.color}'."
        )
    except Exception as e:
        print(f"Error creating label: {e}")
        raise typer.Exit(code=1)


@labels_app.command("delete")
def labels_delete(
    label_id: str = typer.Argument(..., help="The ID of the label to delete."),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Delete a label from a board.
    """
    db: Session = next(get_db())
    board_id = get_board_id(db, board_id)
    # This is a placeholder as py-trello does not support deleting labels directly.
    # A direct API call would be needed.
    print("Deleting labels is not currently supported by the underlying library.")
    print(
        "To delete a label, you need to make a direct DELETE request to the Trello API."
    )
    print(f"Example: DELETE /1/labels/{label_id}")
    raise typer.Exit()


@app.command()
def report(
    days: int = typer.Option(7, help="The number of days to report on."),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Generate a report of board activity.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
    except Exception as e:
        print(f"Error connecting to Trello or finding board: {e}")
        raise typer.Exit(code=1)

    since_date = datetime.now(timezone.utc) - timedelta(days=days)

    # py-trello doesn't have a direct way to filter actions by date,
    # so we have to fetch all and filter locally.
    # For large boards, this could be slow.
    actions = board.fetch_actions(action_filter="all")

    print(f"# Report for board '{board.name}' for the last {days} days")
    print("\n## Cards Created")

    for action in actions:
        action_date = action.get("date")
        if (
            action_date
            and datetime.fromisoformat(action_date.replace("Z", "+00:00")) > since_date
        ):
            if action.get("type") == "createCard":
                card_name = action.get("data", {}).get("card", {}).get("name")
                print(f"- {card_name}")

    print("\n## Cards Moved")
    for action in actions:
        action_date = action.get("date")
        if (
            action_date
            and datetime.fromisoformat(action_date.replace("Z", "+00:00")) > since_date
        ):
            if action.get("type") == "updateCard" and action.get("data", {}).get(
                "listBefore"
            ):
                card_name = action.get("data", {}).get("card", {}).get("name")
                list_before = action.get("data", {}).get("listBefore", {}).get("name")
                list_after = action.get("data", {}).get("listAfter", {}).get("name")
                print(f"- '{card_name}' moved from '{list_before}' to '{list_after}'")

    print("\n## Cards Archived")
    for action in actions:
        action_date = action.get("date")
        if (
            action_date
            and datetime.fromisoformat(action_date.replace("Z", "+00:00")) > since_date
        ):
            if action.get("type") == "updateCard" and action.get("data", {}).get(
                "card", {}
            ).get("closed"):
                card_name = action.get("data", {}).get("card", {}).get("name")
                print(f"- {card_name}")


@app.command(name="ai-label")
def ai_label(
    instructions_file: str = typer.Option(
        None, help="Path to a file with labeling instructions."
    ),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Automatically label unlabeled cards using the Gemini API.
    """
    db: Session = next(get_db())
    board_id = get_board_id(db, board_id)
    gemini_api_key = db.query(Config).filter(Config.key == "GEMINI_API_KEY").first()

    if not gemini_api_key:
        print("Gemini API key not configured. Please run 'trello-cli config gemini'")
        raise typer.Exit(code=1)

    genai.configure(api_key=gemini_api_key.value)

    try:
        client = get_trello_client()
        board = client.get_board(board_id)
    except Exception as e:
        print(f"Error connecting to Trello or finding board: {e}")
        raise typer.Exit(code=1)

    available_labels = {label.name: label for label in board.get_labels()}
    if not available_labels:
        print("No labels found on this board to choose from.")
        return

    label_names = [name for name in available_labels.keys() if not name.isupper()]
    unlabeled_cards = [card for card in board.all_cards() if not card.labels]

    if not unlabeled_cards:
        print("No unlabeled cards found.")
        return

    instructions = ""
    if instructions_file and os.path.exists(instructions_file):
        with open(instructions_file, "r") as f:
            instructions = f.read()

    print(f"Found {len(unlabeled_cards)} unlabeled cards. Analyzing...")

    model = genai.GenerativeModel("gemini-1.5-flash")

    for card in unlabeled_cards:
        print(f"Analyzing card: '{card.name}'")

        prompt = (
            f"Please follow these instructions when assigning labels:\n{instructions}\n\n"
            f"Given the following Trello card title and description, "
            f"which of the following labels are most appropriate?\n\n"
            f"Labels: {', '.join(label_names)}\n\n"
            f"Card Title: {card.name}\n"
            f"Card Description: {card.description}\n\n"
            f"Please respond with a comma-separated list of the best label names."
        )

        try:
            response = model.generate_content(prompt)
            chosen_label_names = [label.strip() for label in response.text.split(",")]
        except Exception as e:
            print(f"Error generating labels for card '{card.name}': {e}")
            chosen_label_names = []

        if chosen_label_names:
            labels_to_apply = [
                available_labels[name]
                for name in chosen_label_names
                if name in available_labels
            ]

            if labels_to_apply:
                for label in labels_to_apply:
                    card.add_label(label)
                print(f"  Applied labels: {', '.join(chosen_label_names)}")
            else:
                print("  No matching labels found to apply.")
        else:
            print("  Could not determine appropriate labels.")


@boards_app.command("show")
def boards_show():
    """Show all boards."""
    try:
        client = get_trello_client()
        boards = client.list_boards()
        for board in boards:
            print(f"Board Name: {board.name}, ID: {board.id}")
    except Exception as e:
        print(f"Error getting boards: {e}")
        raise typer.Exit(code=1)


@boards_app.command("create")
def boards_create(name: str):
    """Create a new board."""
    try:
        client = get_trello_client()
        board = client.add_board(name)
        print(f"Successfully created board '{board.name}' with ID '{board.id}'.")
    except Exception as e:
        print(f"Error creating board: {e}")
        raise typer.Exit(code=1)


@boards_app.command("update")
def boards_update(
    name: str = typer.Option(None, help="The new name for the board."),
    description: str = typer.Option(None, help="The new description for the board."),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """Update a board's name or description."""
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        if name:
            board.set_name(name)
        if description:
            board.set_description(description)
        print(f"Successfully updated board '{board.name}'.")
    except Exception as e:
        print(f"Error updating board: {e}")
        raise typer.Exit(code=1)


@boards_app.command("close")
def boards_close(
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Close a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        board.close()
        print(f"Successfully closed board '{board.name}'.")
    except Exception as e:
        print(f"Error closing board: {e}")
        raise typer.Exit(code=1)


@boards_app.command("lists")
def boards_lists(
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    List all lists on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        lists = board.all_lists()
        print(f"Lists on board '{board.name}':")
        for lst in lists:
            print(f"- {lst.name} (ID: {lst.id})")
    except Exception as e:
        print(f"Error listing lists: {e}")
        raise typer.Exit(code=1)


@boards_app.command("labels")
def boards_labels(
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    List all labels on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        labels = board.get_labels()
        print(f"Labels on board '{board.name}':")
        for label in labels:
            print(f"- {label.name} (ID: {label.id}, Color: {label.color})")
    except Exception as e:
        print(f"Error listing labels: {e}")
        raise typer.Exit(code=1)


@boards_app.command("cards")
def boards_cards(
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    List all cards on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        cards = board.all_cards()
        print(f"Cards on board '{board.name}':")
        for card in cards:
            print(f"- {card.name} (ID: {card.id})")
    except Exception as e:
        print(f"Error listing cards: {e}")
        raise typer.Exit(code=1)


@boards_app.command("members")
def boards_members(
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    List all members of a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        members = board.get_members()
        print(f"Members of board '{board.name}':")
        for member in members:
            print(f"- {member.full_name} (Username: {member.username})")
    except Exception as e:
        print(f"Error listing members: {e}")
        raise typer.Exit(code=1)


@boards_app.command("powerups")
def boards_powerups(
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    List all enabled power-ups on a board.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
        powerups = board.get_powerups()
        print(f"Enabled Power-Ups on board '{board.name}':")
        for powerup in powerups:
            print(f"- {powerup['name']} (ID: {powerup['id']})")
    except Exception as e:
        print(f"Error listing power-ups: {e}")
        raise typer.Exit(code=1)


@cards_app.command("get")
def cards_get(card_id: str):
    """
    Get a card by ID.
    """
    try:
        client = get_trello_client()
        card = client.get_card(card_id)
        print(f"Card Name: {card.name}")
        print(f"Description: {card.description}")
        print(f"URL: {card.url}")
        print(f"List: {card.list_id}")
    except Exception as e:
        print(f"Error getting card: {e}")
        raise typer.Exit(code=1)


@cards_app.command("create")
def cards_create(list_id: str, name: str):
    """
    Create a new card.
    """
    try:
        client = get_trello_client()
        lst = client.get_list(list_id)
        card = lst.add_card(name)
        print(f"Successfully created card '{card.name}' with ID '{card.id}'.")
    except Exception as e:
        print(f"Error creating card: {e}")
        raise typer.Exit(code=1)


@cards_app.command("update")
def cards_update(card_id: str, name: str = None, description: str = None):
    """
    Update a card's name or description.
    """
    try:
        client = get_trello_client()
        card = client.get_card(card_id)
        if name:
            card.set_name(name)
        if description:
            card.set_description(description)
        print(f"Successfully updated card '{card.name}'.")
    except Exception as e:
        print(f"Error updating card: {e}")
        raise typer.Exit(code=1)


@cards_app.command("delete")
def cards_delete(card_id: str):
    """
    Delete a card.
    """
    try:
        client = get_trello_client()
        card = client.get_card(card_id)
        card.delete()
        print(f"Successfully deleted card '{card.name}'.")
    except Exception as e:
        print(f"Error deleting card: {e}")
        raise typer.Exit(code=1)


@cards_app.command("move")
def cards_move(card_id: str, list_id: str):
    """
    Move a card to a different list.
    """
    try:
        client = get_trello_client()
        card = client.get_card(card_id)
        card.change_list(list_id)
        print(f"Successfully moved card '{card.name}' to list '{list_id}'.")
    except Exception as e:
        print(f"Error moving card: {e}")
        raise typer.Exit(code=1)


@cards_app.command("comment")
def cards_comment(card_id: str, text: str):
    """
    Add a comment to a card.
    """
    try:
        client = get_trello_client()
        card = client.get_card(card_id)
        card.comment(text)
        print(f"Successfully added comment to card '{card.name}'.")
    except Exception as e:
        print(f"Error adding comment: {e}")
        raise typer.Exit(code=1)


@cards_app.command("add-label")
def cards_add_label(card_id: str, label_id: str):
    """
    Add a label to a card.
    """
    try:
        client = get_trello_client()
        card = client.get_card(card_id)
        label = client.get_label(label_id, card.board_id)
        card.add_label(label)
        print(f"Successfully added label '{label.name}' to card '{card.name}'.")
    except Exception as e:
        print(f"Error adding label: {e}")
        raise typer.Exit(code=1)


@cards_app.command("remove-label")
def cards_remove_label(card_id: str, label_id: str):
    """
    Remove a label from a card.
    """
    try:
        client = get_trello_client()
        card = client.get_card(card_id)
        label = client.get_label(label_id, card.board_id)
        card.remove_label(label)
        print(f"Successfully removed label '{label.name}' from card '{card.name}'.")
    except Exception as e:
        print(f"Error removing label: {e}")
        raise typer.Exit(code=1)


@app.command()
def export(
    output_file: str = typer.Option(
        "loomic_export.json", help="Output file path for the Loomic export."
    ),
    board_id: str = typer.Option(
        None, "--board-id", "-b", help="The ID of the Trello board."
    ),
):
    """
    Export a Trello board to Loomic backup format.
    """
    db: Session = next(get_db())
    try:
        board_id = get_board_id(db, board_id)
        client = get_trello_client()
        board = client.get_board(board_id)
    except Exception as e:
        print(f"Error connecting to Trello or finding board: {e}")
        raise typer.Exit(code=1)

    print(f"Exporting board '{board.name}' to Loomic format...")

    # Create the Loomic backup structure
    loomic_backup = {
        "timestamp": time.time(),
        "app_version": "1.0",
        "hierarchy": {
            "items": [
                {
                    "type": "board",
                    "name": board.name,
                    "id": str(uuid.uuid4()),
                    "filepath": f"{board.name.replace(' ', '_')}.json",
                }
            ]
        },
        "boards_data": {},
        "notebooks_data": {},
    }

    # Get all lists and cards
    board_lists = board.all_lists()

    # Create the board data structure
    board_data = {
        "board_name": board.name,
        "id": loomic_backup["hierarchy"]["items"][0]["id"],
        "lists": [],
        "tags": [],
        "next_list_id_counter": len(board_lists) + 1,
        "list_creation_counter": len(board_lists),
        "notebook_documents": [],
    }

    # Convert Trello lists to Loomic format
    for i, trello_list in enumerate(board_lists):
        loomic_list = {
            "id": f"list_{i + 1}",
            "title": trello_list.name,
            "header_color": "#FFFACD",  # Default light yellow color
            "cards": [],
        }

        # Get cards in this list
        cards = trello_list.list_cards()

        for card in cards:
            # Convert Trello date format to Loomic format
            start_date = None
            due_date = None
            date_completed = None

            if hasattr(card, "due_date") and card.due_date:
                due_date = card.due_date.strftime("%Y-%m-%d")

            # Determine if card is complete based on its list name or labels
            is_complete = False
            if trello_list.name.lower() in ["done", "completed", "finished", "archive"]:
                is_complete = True
                date_completed = datetime.now().strftime("%Y-%m-%d")

            # Convert card labels to tags
            tags = []
            if card.labels:
                tags = [label.name for label in card.labels if label.name]

            # Generate a 32-character hex ID (similar to Loomic format)
            card_id = card.id.ljust(32, "0")[:32]

            loomic_card = {
                "id": card_id,
                "text": card.name,
                "color": "default",
                "is_complete": is_complete,
                "start_date": start_date,
                "due_date": due_date,
                "date_completed": date_completed,
                "timer_start_time_ts": None,
                "timer_total_elapsed_seconds": 0,
                "timer_is_paused": False,
                "timer_is_active": False,
                "timer_locked_display_time": None,
                "notebook_link": None,
                "tags": tags,
            }

            loomic_list["cards"].append(loomic_card)

        board_data["lists"].append(loomic_list)

    # Add board data to the backup structure
    board_filename = loomic_backup["hierarchy"]["items"][0]["filepath"]
    loomic_backup["boards_data"][board_filename] = board_data

    # Write the export file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(loomic_backup, f, indent=2, ensure_ascii=False)

        print(f"Successfully exported board '{board.name}' to '{output_file}'")
        print(
            f"Exported {len(board_lists)} lists with {sum(len(lst['cards']) for lst in board_data['lists'])} total cards"
        )

    except Exception as e:
        print(f"Error writing export file: {e}")
        raise typer.Exit(code=1)


@app.command("help", help="Display help for all commands")
def help_command(ctx: typer.Context):
    """
    Shows help for all commands and subcommands.
    """
    console = Console()

    # Main application help
    main_help = ctx.parent.get_help()
    console.print(main_help)

    # Sub-applications help
    for sub_app_info in app.registered_groups:
        console.print(f"\n[bold cyan]Help for: {sub_app_info.name}[/bold cyan]")

        from typer.main import get_command

        cmd = get_command(sub_app_info.typer_instance)

        # Create a Rich renderable for the help text
        sub_ctx = typer.Context(cmd)
        console.print(sub_ctx.get_help())


if __name__ == "__main__":
    app()
