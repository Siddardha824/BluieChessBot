from pathlib import Path
from gui.utils import get_logger


logger = get_logger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

GUI_DIR = ROOT_DIR

ASSETS_DIR = GUI_DIR / "assets"

ICONS_DIR = ASSETS_DIR / "icons"

SPACE_DOWN_ARROW_ICON = ICONS_DIR / "space_down_arrow.svg"
SPACE_SPIN_UP_ARROW_ICON = ICONS_DIR / "space_spin_up_arrow.svg"
SPACE_SPIN_DOWN_ARROW_ICON = ICONS_DIR / "space_spin_down_arrow.svg"

SPRITE_SHEET = ASSETS_DIR / "Pieces.png"

PREFERENCES_FILE = ROOT_DIR / "config" / "preferences.json"

STYLES_DIR = ROOT_DIR / "app" / "theme" / "styles"

logger.debug("Application root directory: %s", ROOT_DIR)
