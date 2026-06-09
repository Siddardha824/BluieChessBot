import json
from gui.app.shared.paths import PREFERENCES_FILE
from gui.utils import get_logger


logger = get_logger(__name__)

class PreferencesService:
    @staticmethod
    def load() -> dict:
        path = PREFERENCES_FILE
        if not path.exists():
            logger.info("Preferences file not found; using defaults: %s", path)
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                preferences = json.load(f)
                logger.info("Preferences loaded: %s", path)
                return preferences
        except Exception:
            logger.exception("Failed to load preferences: %s", path)
            return {}

    @staticmethod
    def save(data: dict) -> bool:
        path = PREFERENCES_FILE
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info("Preferences saved: %s", path)
            return True
        except Exception:
            logger.exception("Failed to save preferences: %s", path)
            return False
