from pathlib import Path
from gui.utils import get_logger


logger = get_logger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

GUI_DIR = ROOT_DIR

ASSETS_DIR = GUI_DIR / "assets"

SPRITE_SHEET = ASSETS_DIR / "Pieces.png"

PREFERENCES_FILE = ROOT_DIR / "config" / "preferences.json"

STYLES_DIR = ROOT_DIR / "app" / "theme" / "styles"

logger.debug("Application root directory: %s", ROOT_DIR)

