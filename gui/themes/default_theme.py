# gui/themes/default_theme.py

from dataclasses import dataclass, field
from PySide6.QtGui import QColor
from . import colors

@dataclass
class DefaultTheme:
    # Square Colors
    light_square: QColor = field(default_factory=lambda: colors.LIGHT_SQUARE)
    dark_square: QColor = field(default_factory=lambda: colors.DARK_SQUARE)
    
    # Highlight Colors
    selection: QColor = field(default_factory=lambda: colors.SELECTION_COLOR)
    legal_move: QColor = field(default_factory=lambda: colors.LEGAL_MOVE_COLOR)
    last_move: QColor = field(default_factory=lambda: colors.LAST_MOVE_COLOR)
    check: QColor = field(default_factory=lambda: colors.CHECK_COLOR)
    
    # Label Text Colors (for board coordinates)
    text_on_light: QColor = field(default_factory=lambda: colors.TEXT_LIGHT_SQUARE)
    text_on_dark: QColor = field(default_factory=lambda: colors.TEXT_DARK_SQUARE)

    # Panel UI Colors
    panel_background: QColor = field(default_factory=lambda: colors.PANEL_BG)
    panel_text: QColor = field(default_factory=lambda: colors.PANEL_TEXT)
    panel_text_muted: QColor = field(default_factory=lambda: colors.PANEL_TEXT_MUTED)

    # Console UI Colors
    console_in: QColor = field(default_factory=lambda: colors.CONSOLE_IN)
    console_out: QColor = field(default_factory=lambda: colors.CONSOLE_OUT)
    console_info: QColor = field(default_factory=lambda: colors.CONSOLE_INFO)
    console_error: QColor = field(default_factory=lambda: colors.CONSOLE_ERROR)

    # Evaluation Bar UI Colors
    eval_white: QColor = field(default_factory=lambda: colors.EVAL_WHITE)
    eval_black: QColor = field(default_factory=lambda: colors.EVAL_BLACK)

    # Border UI Colors
    panel_border: QColor = field(default_factory=lambda: colors.PANEL_BORDER)

    # Fonts and sizes
    font_family: str = "Outfit"
    font_size: int = 11
