# gui/themes/theme_manager.py

from PySide6.QtGui import QColor
from .active_theme import ActiveTheme
from . import colors
from gui.core.config import ACTIVE_THEME


# Preset active theme instances mapped directly to colors.py tokens
LICHESS_THEME = ActiveTheme(
    name="LiChess Blue/Grey",
    light_square=colors.LIGHT_SQUARE,
    dark_square=colors.DARK_SQUARE,
    selection=colors.SELECTION_COLOR,
    legal_move=colors.LEGAL_MOVE_COLOR,
    last_move=colors.LAST_MOVE_COLOR,
    check=colors.CHECK_COLOR,
    debug_overlay_white=colors.CONSOLE_INFO,    # White attacks uses console info color
    debug_overlay_black=colors.CONSOLE_ERROR,   # Black attacks uses console error color
    debug_overlay_legals=QColor(124, 77, 255, 100),
    text_on_light=colors.TEXT_LIGHT_SQUARE,
    text_on_dark=colors.TEXT_DARK_SQUARE,
    panel_background=colors.PANEL_BG,
    panel_text=colors.PANEL_TEXT,
    panel_text_muted=colors.PANEL_TEXT_MUTED,
    panel_border=colors.PANEL_BORDER,
    console_in=colors.CONSOLE_IN,
    console_out=colors.CONSOLE_OUT,
    console_info=colors.CONSOLE_INFO,
    console_error=colors.CONSOLE_ERROR,
    eval_white=colors.EVAL_WHITE,
    eval_black=colors.EVAL_BLACK
)

BLUIE_QUANTUM_THEME = ActiveTheme(
    name="Bluie Quantum (Signature)",
    light_square=colors.QUANTUM_LIGHT_SQUARE,
    dark_square=colors.QUANTUM_DARK_SQUARE,
    selection=colors.QUANTUM_SELECTION,
    legal_move=colors.QUANTUM_LEGAL_MOVE,
    last_move=colors.QUANTUM_LAST_MOVE,
    check=colors.QUANTUM_CHECK,
    debug_overlay_white=colors.QUANTUM_CONSOLE_IN,
    debug_overlay_black=colors.QUANTUM_CONSOLE_ERROR,
    debug_overlay_legals=QColor(124, 77, 255, 100),
    text_on_light=colors.QUANTUM_TEXT_LIGHT,
    text_on_dark=colors.QUANTUM_TEXT_DARK,
    panel_background=colors.QUANTUM_PANEL_BG,
    panel_text=colors.QUANTUM_PANEL_TEXT,
    panel_text_muted=colors.QUANTUM_PANEL_TEXT_MUTED,
    panel_border=colors.QUANTUM_PANEL_BORDER,
    console_in=colors.QUANTUM_CONSOLE_IN,
    console_out=colors.QUANTUM_CONSOLE_OUT,
    console_info=colors.QUANTUM_CONSOLE_INFO,
    console_error=colors.QUANTUM_CONSOLE_ERROR,
    eval_white=colors.QUANTUM_EVAL_WHITE,
    eval_black=colors.QUANTUM_EVAL_BLACK
)

FOREST_GREEN_THEME = ActiveTheme(
    name="Classic Forest Green",
    light_square=colors.GREEN_LIGHT_SQUARE,
    dark_square=colors.GREEN_DARK_SQUARE,
    selection=colors.GREEN_SELECTION,
    legal_move=colors.GREEN_LEGAL_MOVE,
    last_move=colors.GREEN_LAST_MOVE,
    check=colors.GREEN_CHECK,
    debug_overlay_white=colors.GREEN_CONSOLE_IN,
    debug_overlay_black=colors.GREEN_CONSOLE_ERROR,
    debug_overlay_legals=QColor(124, 77, 255, 100),
    text_on_light=colors.GREEN_TEXT_LIGHT,
    text_on_dark=colors.GREEN_TEXT_DARK,
    panel_background=colors.GREEN_PANEL_BG,
    panel_text=colors.GREEN_PANEL_TEXT,
    panel_text_muted=colors.GREEN_PANEL_TEXT_MUTED,
    panel_border=colors.GREEN_PANEL_BORDER,
    console_in=colors.GREEN_CONSOLE_IN,
    console_out=colors.GREEN_CONSOLE_OUT,
    console_info=colors.GREEN_CONSOLE_INFO,
    console_error=colors.GREEN_CONSOLE_ERROR,
    eval_white=colors.GREEN_EVAL_WHITE,
    eval_black=colors.GREEN_EVAL_BLACK
)


class ThemeManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.themes = {
            "LICHESS_BLUE": LICHESS_THEME,
            "BLUIE_QUANTUM": BLUIE_QUANTUM_THEME,
            "FOREST_GREEN": FOREST_GREEN_THEME
        }
        self._current_theme_name = ACTIVE_THEME
        self._initialized = True

    def get_theme(self) -> ActiveTheme:
        """Returns the active ActiveTheme configuration based on settings."""
        return self.themes.get(self._current_theme_name, BLUIE_QUANTUM_THEME)

    def set_theme(self, name: str) -> None:
        """Sets a new active theme by name string key."""
        if name in self.themes:
            self._current_theme_name = name

# Shared theme manager singleton
theme_manager = ThemeManager()
