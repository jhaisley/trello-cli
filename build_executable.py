#!/usr/bin/env python3
"""
Build script to create a standalone executable using PyInstaller.
This allows distribution without requiring Python to be installed.
"""

import importlib.util
import subprocess
import sys


def build_executable():
    """Build a standalone executable using PyInstaller."""

    # Install PyInstaller if not available
    if importlib.util.find_spec("PyInstaller") is None:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name",
        "trello-cli",
        "--console",
        "src/trello_cli/main.py",
    ]

    print("Building standalone executable...")
    subprocess.check_call(cmd)

    print("Executable built successfully!")
    print("Find it in: dist/trello-cli.exe")


if __name__ == "__main__":
    build_executable()
