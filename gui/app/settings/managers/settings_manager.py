from PySide6.QtCore import QObject, Signal
from ..services.preferences_service import PreferencesService
from gui.utils import get_logger

logger = get_logger(__name__)

class SettingsManager(QObject):
    saved = Signal()
    loaded = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        self.load()
        logger.info("Settings manager initialized")

    def save(self, **kwargs):
        if kwargs:
            success = PreferencesService.save(self._settings, kwargs)
            if success:
                self.saved.emit()

    def load(self):
        self._settings = PreferencesService.load()

        if self._settings is not None:
            self.loaded.emit(self._settings)
