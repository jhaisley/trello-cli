#!/usr/bin/env python3
"""
Entry point for the trello-tools executable.
This file is used by PyInstaller to create the standalone executable.
"""

import os
import sys

# Add the src directory to the Python path
if hasattr(sys, "_MEIPASS"):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))

src_path = os.path.join(base_path, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

if __name__ == "__main__":
    from trello_cli.main import app

    app()
