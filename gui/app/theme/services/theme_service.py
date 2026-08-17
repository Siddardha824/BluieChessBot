"""Theme rendering and stylesheet application service.

This module provides the ThemeService class, which loads, compiles, and applies
stylesheet configurations to the Qt application instance.
"""

import dataclasses
from PySide6.QtWidgets import QApplication
from gui.app.shared import (
    SPACE_DOWN_ARROW_ICON,
    SPACE_SPIN_DOWN_ARROW_ICON,
    SPACE_SPIN_UP_ARROW_ICON,
    STYLESHEET
)

from .constants import PRESET_THEMES
from ..models.theme_state import ThemeState
from gui.utils import get_logger

logger = get_logger(__name__)


class ThemeService:
    """
    Service for loading themes and applying stylesheets.

    This service replaces placeholders in stylesheet templates with concrete theme
    colors and asset file paths, then binds them to the active QApplication.
    """

    def __init__(self):
        """Initialize the theme service."""
        self._qss = STYLESHEET

    @property
    def available_themes(self) -> list[str]:
        """Return the list of all available preset theme names."""
        return list(PRESET_THEMES.keys())

    def load_presets(self) -> dict[str, ThemeState]:
        """Load and return the list of preset themes.

        Returns:
            A dictionary mapping preset names to ThemeState objects.
        """
        return PRESET_THEMES

    def apply_stylesheet(self, theme: ThemeState) -> bool:
        """Process and apply a stylesheet with theme values.

        Args:
            theme: The target ThemeState defining placeholder color values.

        Returns:
            True if the stylesheet was applied successfully, False otherwise.
        """
        try:
            with open(self._qss, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
        except Exception:
            logger.exception("Failed to load stylesheet.qss")
            return False

        theme_dic = dataclasses.asdict(theme)

        for key, value in theme_dic.items():
            if value is not None:
                placeholder = f"{{{{ {key} }}}}"
                stylesheet = stylesheet.replace(placeholder, str(value))

        stylesheet = stylesheet.replace("__SPACE_DOWN_ARROW_ICON__", SPACE_DOWN_ARROW_ICON.as_posix())
        stylesheet = stylesheet.replace("__SPACE_SPIN_UP_ARROW_ICON__", SPACE_SPIN_UP_ARROW_ICON.as_posix())
        stylesheet = stylesheet.replace("__SPACE_SPIN_DOWN_ARROW_ICON__", SPACE_SPIN_DOWN_ARROW_ICON.as_posix())

        # Verify a valid QApplication instance is running to prevent crashes during headless testing
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(stylesheet)
        else:
            logger.error("Unable to apply the stylesheet")
            return False

        logger.info("Theme set to %s", theme.name)

        return True
