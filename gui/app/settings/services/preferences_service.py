import json
from gui.app.shared.paths import PREFERENCES_FILE
from gui.utils import get_logger

logger = get_logger(__name__)

class PreferencesService:
    @staticmethod
    def load() -> dict | None:
        path = PREFERENCES_FILE

        if not path.exists():
            logger.info("Preferences File Not found")
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info("Preferences loaded: %s", path)
                return data
        except Exception:
            logger.exception("Failed to load Preferences File")
            return None

    @staticmethod
    def save(settings: dict | None, new_settings: dict) -> bool:
        if settings is not None:
            for key, val in new_settings.items():
                settings[key] = val
        else:
            settings = new_settings
        path = PREFERENCES_FILE

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            logger.info("Preferences saved: %s", path)
            return True
        except Exception:
            logger.exception("Failed to save the preferences")
            return False
