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

    # Fonts and sizes
    font_family: str = "Outfit"
    font_size: int = 11
