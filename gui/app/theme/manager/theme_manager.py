"""Application theme manager facade module.

This module provides the ThemeManager class, which coordinates loading,
modifying, applying, and exporting stylesheet theme configurations across the GUI.
"""

import dataclasses
from PySide6.QtCore import QObject, Signal
from ..services.theme_service import ThemeService
from ..models.theme_state import ThemeState
from gui.utils import get_logger

logger = get_logger(__name__)


class ThemeManager(QObject):
    """
    Controller facade for managing and applying application themes.

    This manager orchestrates loading preset and custom themes, applying active
    stylesheets to the application, and emitting signals to notify reactive observers.

    Signals:
        theme_changed (Signal): Emitted when the active application ThemeState changes.
    """

    # Emitted when the active application theme changes. Payload: theme (ThemeState)
    theme_changed = Signal(ThemeState)

    def __init__(self, parent, name="space"):
        """Initialize the theme manager.

        Args:
            parent: Qt parent object for memory management.
            name: The name of the preset theme to load initially.
        """
        super().__init__(parent)

        self._theme_service = ThemeService()

        self.load_theme(name)

        logger.info("Theme Manager Initialized")

    def load_theme(self, theme_name: str):
        """Load a preset theme by name and apply it.

        Args:
            theme_name: The name identifier of the preset theme to load.
        """
        presets = self._load_presets()

        if theme_name in presets.keys():
            self._active_theme = presets[theme_name]
            self.apply_theme(self._active_theme)

    def load_theme_from_settings(self, theme_dict: dict):
        """Load and apply a custom theme representation from a dictionary.

        Args:
            theme_dict: Dictionary representation of the target ThemeState.
        """
        theme = ThemeState.from_dict(theme_dict)

        self._active_theme = theme
        self.apply_theme(theme)

    @property
    def available_themes(self) -> list[str]:
        """Return the list of available preset theme names."""
        return self._theme_service.available_themes

    @property
    def active_theme_name(self) -> str:
        """Return the name of the active theme."""
        return self._active_theme.name

    def _load_presets(self) -> dict[str, ThemeState]:
        """Load and return all available preset configurations.

        Returns:
            A dictionary mapping preset name strings to ThemeState objects.
        """
        return self._theme_service.load_presets()

    def apply_theme(self, theme: ThemeState):
        """Apply a ThemeState stylesheet configuration to the application.

        Args:
            theme: The ThemeState configuration to apply.
        """
        success = self._theme_service.apply_stylesheet(theme)

        if success:
            self.theme_changed.emit(theme)

    def get_export_state(self) -> dict:
        """Export the active theme state as a dictionary.

        Returns:
            A dictionary representation of the active ThemeState.
        """
        return dataclasses.asdict(self._active_theme)
