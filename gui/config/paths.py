from pathlib import Path


# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


# GUI directory
GUI_DIR = ROOT_DIR / "gui"


# Assets directory
ASSETS_DIR = GUI_DIR / "assets"


# Piece assets
SPRITE_SHEET = ASSETS_DIR / "Pieces.png"