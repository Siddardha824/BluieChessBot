from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

GUI_DIR = ROOT_DIR / "gui_new"

ASSETS_DIR = GUI_DIR / "assets"

SPRITE_SHEET = ASSETS_DIR / "Pieces.png"

PREFERENCES_FILE = ROOT_DIR / "preferences.json"

