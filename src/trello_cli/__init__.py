"""
Trello Tools - A powerful CLI for managing Trello boards, cards, and labels.

This package provides a comprehensive command-line interface for interacting with Trello,
including features for board management, card operations, label management, and AI-powered
automation using Google Gemini.
"""

__version__ = "0.3.0"
__author__ = "Jordan Haisley"
__email__ = "jordanhaisley@google.com"

# Make version easily accessible
from .main import app

__all__ = ["app", "__version__"]
