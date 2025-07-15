from trello import TrelloClient
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Config

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_trello_client() -> TrelloClient:
    """
    Initializes and returns the Trello client using credentials from the database.
    """
    db: Session = next(get_db())
    
    api_key = db.query(Config).filter(Config.key == "TRELLO_API_KEY").first()
    api_secret = db.query(Config).filter(Config.key == "TRELLO_API_SECRET").first()
    token = db.query(Config).filter(Config.key == "TRELLO_TOKEN").first()

    if not all([api_key, api_secret, token]):
        raise ValueError("Trello API credentials not configured. Please run 'trello-cli config'")

    return TrelloClient(
        api_key=api_key.value,
        api_secret=api_secret.value,
        token=token.value
    )
