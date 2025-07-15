import os
import sys
from trello import TrelloClient
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.expanduser("~/.env"))

# Get Trello API credentials from environment variables
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_API_SECRET = os.getenv("TRELLO_API_SECRET")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_trello_client():
    """Initializes and returns the Trello client."""
    return TrelloClient(
        api_key=TRELLO_API_KEY,
        api_secret=TRELLO_API_SECRET,
        token=TRELLO_TOKEN
    )

def get_board_by_id(client, board_id):
    """Finds a Trello board by its ID."""
    try:
        return client.get_board(board_id)
    except Exception as e:
        print(f"Error getting board '{board_id}': {e}")
        return None

def get_available_labels(board):
    """Fetches all available labels for a given board."""
    return {label.name: label for label in board.get_labels()}

def get_unlabeled_cards(board):
    """Fetches all cards with no labels from a given board."""
    return [card for card in board.all_cards() if not card.labels]

def choose_labels_with_ai(card, label_names, instructions):
    """
    Uses the Gemini API to choose the most appropriate labels for a card.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')

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
        return [label.strip() for label in response.text.split(',')]
    except Exception as e:
        print(f"Error generating labels for card '{card.name}': {e}")
        return []

def main():
    """
    Main function to fetch unlabeled cards, analyze them with AI,
    and apply the most appropriate labels.
    """
    if len(sys.argv) != 2:
        print("Usage: python tlabeler.py 'Your Board ID'")
        sys.exit(1)

    board_id = sys.argv[1]

    client = get_trello_client()
    board = get_board_by_id(client, board_id)

    if not board:
        print(f"Error: Board with ID '{board_id}' not found.")
        sys.exit(1)

    available_labels = get_available_labels(board)
    if not available_labels:
        print("No labels found on this board to choose from.")
        return

    label_names = [name for name in available_labels.keys() if not name.isupper()]
    unlabeled_cards = get_unlabeled_cards(board)

    if not unlabeled_cards:
        print("No unlabeled cards found.")
        return

    instructions = ""
    instructions_path = os.path.join(os.path.dirname(__file__), 'instructions.md')
    if os.path.exists(instructions_path):
        with open(instructions_path, 'r') as f:
            instructions = f.read()

    print(f"Found {len(unlabeled_cards)} unlabeled cards. Analyzing...")

    for card in unlabeled_cards:
        print(f"Analyzing card: '{card.name}'")
        chosen_label_names = choose_labels_with_ai(card, label_names, instructions)

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

if __name__ == "__main__":
    main()
