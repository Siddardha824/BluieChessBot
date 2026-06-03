from PySide6.QtCore import QObject, Signal

from .active_theme import ActiveTheme

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
            return

        self._theme = theme
        self.theme_changed.emit(theme)