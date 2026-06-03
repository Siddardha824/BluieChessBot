import json
from gui_new.modules.shared.constants import PREFERENCES_FILE

class PreferencesService:
    @staticmethod
    def load() -> dict:
        path = PREFERENCES_FILE
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save(data: dict) -> bool:
        path = PREFERENCES_FILE
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception:
            return False