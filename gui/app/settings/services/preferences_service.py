"""Preferences load and save service.

This module provides the PreferencesService utility class, which manages loading
and writing application configuration preferences on disk using JSON format.
"""

import json
from gui.app.shared.paths import PREFERENCES_FILE
from gui.utils import get_logger

logger = get_logger(__name__)


class PreferencesService:
    """Provide static utility methods for managing application preferences.

    This class handles the serialization of settings dictionary payloads to JSON
    format and manages writing/reading them to the user configurations directory.
    """

    @staticmethod
    def load() -> dict | None:
        """Load configuration preferences from the file system.

        Returns:
            A dictionary containing loaded preferences, or None if not found or failed.
        """
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
        """Save configuration preferences to the file system.

        If an existing settings dictionary is provided, merge new preferences
        into it. Otherwise, create a new settings structure.

        Args:
            settings: Existing preferences dictionary to merge with, or None.
            new_settings: Dictionary of new preferences to update or save.

        Returns:
            True if the preferences were successfully saved, False otherwise.
        """
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
