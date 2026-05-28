# gui/core/config.py

from pathlib import Path

# Project root directory (three parents up from gui/core/config.py)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# GUI directory
GUI_DIR = ROOT_DIR / "gui"

# Assets directory
ASSETS_DIR = GUI_DIR / "assets"

# Piece spritesheet asset path
SPRITE_SHEET = ASSETS_DIR / "Pieces.png"

# Active UI Theme Name
ACTIVE_THEME = "BLUIE_QUANTUM"  # Pre-defined options: "LICHESS_BLUE", "BLUIE_QUANTUM", "FOREST_GREEN"

