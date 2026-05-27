# gui/themes/default_theme.py

from PySide6.QtGui import QColor
from . import colors

class DefaultTheme:
    def __init__(self):
        # Square Colors
        self.light_square: QColor = colors.LIGHT_SQUARE
        self.dark_square: QColor = colors.DARK_SQUARE
        
        # Highlight Colors
        self.selection: QColor = colors.SELECTION_COLOR
        self.legal_move: QColor = colors.LEGAL_MOVE_COLOR
        self.last_move: QColor = colors.LAST_MOVE_COLOR
        self.check: QColor = colors.CHECK_COLOR
        
        # Label Text Colors (for board coordinates)
        self.text_on_light: QColor = colors.TEXT_LIGHT_SQUARE
        self.text_on_dark: QColor = colors.TEXT_DARK_SQUARE

        # Fonts and sizes
        self.font_family: str = "Outfit"
        self.font_size: int = 11
