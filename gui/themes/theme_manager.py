# gui/themes/theme_manager.py

from dataclasses import dataclass, field
from PySide6.QtGui import QColor
from . import colors

@dataclass
class ThemePalette:
    name: str
    
    # Chessboard Squares
    light_square: QColor
    dark_square: QColor
    
    # Highlights
    selection: QColor
    legal_move: QColor
    last_move: QColor
    check: QColor
    debug_overlay_white: QColor
    debug_overlay_black: QColor
    debug_overlay_legals: QColor
    
    # Board Labels
    text_on_light: QColor
    text_on_dark: QColor
    
    # Panel UI
    panel_background: QColor
    panel_text: QColor
    panel_text_muted: QColor
    panel_border: QColor
    
    # Console
    console_in: QColor
    console_out: QColor
    console_info: QColor
    console_error: QColor
    
    # Evaluation Bar
    eval_white: QColor
    eval_black: QColor
    
    font_family: str = "Outfit"
    font_size: int = 11


# Preset Palette Definitions
LICHESS_THEME = ThemePalette(
    name="LiChess Blue/Grey",
    light_square=QColor("#EFEFED"),
    dark_square=QColor("#70A2CA"),
    selection=QColor(247, 247, 105, 130),
    legal_move=QColor(25, 45, 65, 120),
    last_move=QColor(255, 255, 150, 100),
    check=QColor(240, 80, 80, 140),
    debug_overlay_white=QColor(0, 191, 165, 80),
    debug_overlay_black=QColor(239, 83, 80, 80),
    debug_overlay_legals=QColor(124, 77, 255, 100),
    text_on_light=QColor("#70A2CA"),
    text_on_dark=QColor("#EFEFED"),
    panel_background=QColor("#1E1E1E"),
    panel_text=QColor("#D4D4D4"),
    panel_text_muted=QColor("#888888"),
    panel_border=QColor("#3F3F3F"),
    console_in=QColor("#4FC1FF"),
    console_out=QColor("#9CDCFE"),
    console_info=QColor("#B5CEA8"),
    console_error=QColor("#F44336"),
    eval_white=QColor("#EFEFED"),
    eval_black=QColor("#313131")
)

BLUIE_QUANTUM_THEME = ThemePalette(
    name="Bluie Quantum (Signature)",
    light_square=QColor("#D8D2EC"),          # Lavender Space Dust
    dark_square=QColor("#2B1D61"),           # Quantum Indigo/Violet
    selection=QColor(0, 229, 255, 120),      # Pulsing Neon Cyan Selection
    legal_move=QColor(0, 229, 255, 100),     # Glowing Cyan Legal Dot
    last_move=QColor(124, 77, 255, 90),      # Translucent Space Purple
    check=QColor(255, 64, 129, 140),         # Cosmic Hot Pink Check
    debug_overlay_white=QColor(0, 191, 165, 80),
    debug_overlay_black=QColor(239, 83, 80, 80),
    debug_overlay_legals=QColor(124, 77, 255, 100),
    text_on_light=QColor("#2B1D61"),
    text_on_dark=QColor("#D8D2EC"),
    panel_background=QColor("#0B0813"),      # Deep obsidian panel base
    panel_text=QColor("#E0F7FA"),            # Arctic Silver text
    panel_text_muted=QColor("#78909C"),      # Cool slate gray muted text
    panel_border=QColor("#00E5FF"),          # Sleek Neon Cyan border
    console_in=QColor("#00E5FF"),            # Vibrant Neon Cyan stream
    console_out=QColor("#E040FB"),           # Electric Fuchsia stream
    console_info=QColor("#B2FF59"),          # Bright Lime telemetry
    console_error=QColor("#FF1744"),         # Hot Neon Red alerts
    eval_white=QColor("#D8D2EC"),
    eval_black=QColor("#120E22")
)

FOREST_GREEN_THEME = ThemePalette(
    name="Classic Forest Green",
    light_square=QColor("#FFFFDD"),
    dark_square=QColor("#86A666"),
    selection=QColor(247, 247, 105, 130),
    legal_move=QColor(50, 80, 40, 120),
    last_move=QColor(255, 255, 150, 100),
    check=QColor(240, 80, 80, 140),
    debug_overlay_white=QColor(0, 191, 165, 80),
    debug_overlay_black=QColor(239, 83, 80, 80),
    debug_overlay_legals=QColor(124, 77, 255, 100),
    text_on_light=QColor("#86A666"),
    text_on_dark=QColor("#FFFFDD"),
    panel_background=QColor("#1C2321"),
    panel_text=QColor("#D8F3DC"),
    panel_text_muted=QColor("#74C69D"),
    panel_border=QColor("#2D6A4F"),
    console_in=QColor("#74C69D"),
    console_out=QColor("#95D5B2"),
    console_info=QColor("#D8F3DC"),
    console_error=QColor("#FF87AB"),
    eval_white=QColor("#FFFFDD"),
    eval_black=QColor("#1B4332")
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
        self._current_theme_name = "BLUIE_QUANTUM"
        self._initialized = True

    def get_theme(self) -> ThemePalette:
        """Returns the active ThemePalette object based on settings."""
        return self.themes.get(self._current_theme_name, BLUIE_QUANTUM_THEME)

    def set_theme(self, name: str) -> None:
        """Sets a new active theme by name string key."""
        if name in self.themes:
            self._current_theme_name = name

# Shared theme manager singleton
theme_manager = ThemeManager()
