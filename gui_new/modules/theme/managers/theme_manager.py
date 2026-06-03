from PySide6.QtCore import QObject, Signal

from ..models.theme_state import ThemeState
from ..presets.space_theme import SPACE_THEME
from ..presets.lichess_theme import LICHESS_THEME
from ..presets.chess_com_theme import CHESSCOM_THEME

class ThemeManager(QObject):
    theme_updated = Signal(object)

    _instance = None

    @classmethod
    def get_instance(cls) -> 'ThemeManager':
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)

        self._available_themes = {
            "Space": SPACE_THEME,
            "Lichess": LICHESS_THEME,
            "Chess.com Classic": CHESSCOM_THEME,
        }

        self._theme_state = ThemeState(SPACE_THEME, self)
        self._theme_state.theme_changed.connect(self.theme_updated.emit)

    @property
    def active_theme(self):
        return self._theme_state.theme
    
    @property
    def active_theme_name(self):
        return self._theme_state.theme.name
    
    def set_active_theme(self, theme_name: str):
        theme = self._available_themes.get(theme_name)
        if theme is not None:
            self._theme_state.set_theme(theme)
