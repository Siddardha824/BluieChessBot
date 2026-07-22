import dataclasses
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from ..services.theme_sevice import ThemeService
from ..models.theme_state import ThemeState
from gui.utils import get_logger

logger = get_logger(__name__)

class ThemeManager(QObject):

    theme_changed = Signal(ThemeState)

    def __init__(self, parent, name="space"):
        super().__init__(parent)

        self._theme_service = ThemeService()

        self.load_theme(name)

        logger.info("Theme Manager Initialized")

    def load_theme(self, theme_name):
        presets = self._load_presets()

        if theme_name in presets.keys():
            self._active_theme = presets[theme_name]
            self.apply_theme(self._active_theme)

    def load_theme_from_settings(self, theme_dict: dict):
        theme = ThemeState.from_dict(theme_dict)

        self._active_theme = theme
        self.apply_theme(theme)

    def _load_presets(self) -> dict[str, ThemeState]:
        return self._theme_service.load_presets()

    def apply_theme(self, theme: ThemeState):
        success = self._theme_service.apply_stylesheet(theme)

        if success:
            self.theme_changed.emit(theme)

    def get_export_state(self) -> dict:
        return dataclasses.asdict(self._active_theme)

