"""Application settings manager facade module.

This module provides the SettingsManager class, which serves as a reactive controller
interface for managing and updating persistent user configuration preferences.
"""

from PySide6.QtCore import QObject, Signal
from ..services.preferences_service import PreferencesService
from gui.utils import get_logger

logger = get_logger(__name__)


class SettingsManager(QObject):
    """Provide a controller facade for managing user configuration settings.

    This manager acts as the runtime registry for settings, orchestrating load
    and save transactions, and emitting signals to notify reactive observers.

    Signals:
        saved: Emitted when configuration settings are successfully saved.
        loaded: Emitted with a dict when configuration settings are loaded.
    """

    saved = Signal()
    loaded = Signal(dict)

    def __init__(self, parent):
        """Initialize the settings manager.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)

        self.load()
        logger.info("Settings manager initialized")

    def save(self, **kwargs):
        """Save updated configuration preferences to persistent storage.

        Args:
            **kwargs: Key-value settings pairs to update or create.
        """
        if kwargs:
            success = PreferencesService.save(self._settings, kwargs)
            if success:
                self.saved.emit()

    def load(self):
        """Load configuration preferences from persistent storage."""
        self._settings = PreferencesService.load()

        if self._settings is not None:
            self.loaded.emit(self._settings)
