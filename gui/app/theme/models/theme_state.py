from PySide6.QtCore import QObject, Signal

from .active_theme import ActiveTheme
from gui.utils import get_logger


logger = get_logger(__name__)

class ThemeState(QObject):
    theme_changed = Signal(object)

    def __init__(self, theme: ActiveTheme, parent=None):
        super().__init__(parent)

        self._theme = theme

    @property
    def theme(self) -> ActiveTheme:
        return self._theme

    def set_theme(self, theme: ActiveTheme):
        if self._theme is theme:
            logger.debug("Theme unchanged: %s", theme.name)
            return

        self._theme = theme
        logger.info("Theme changed: %s", theme.name)
        self.theme_changed.emit(theme)
