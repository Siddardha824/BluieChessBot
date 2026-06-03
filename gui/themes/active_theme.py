from dataclasses import dataclass
from PySide6.QtGui import QColor

@dataclass
class ActiveTheme:
    name: str
    
    # Square Colors
    light_square: QColor
    dark_square: QColor
    
    # Highlight Colors
    selection: QColor
    legal_move: QColor
    last_move: QColor
    check: QColor
    
    # Debug Overlay Colors
    debug_overlay_white: QColor
    debug_overlay_black: QColor
    debug_overlay_legals: QColor
    
    # Label Text Colors (for board coordinates)
    text_on_light: QColor
    text_on_dark: QColor

    # Panel UI Colors
    panel_background: QColor
    panel_text: QColor
    panel_text_muted: QColor
    panel_border: QColor

    # Console UI Colors
    console_in: QColor
    console_out: QColor
    console_info: QColor
    console_error: QColor

    # Evaluation Bar UI Colors
    eval_white: QColor
    eval_black: QColor

    # Fonts and sizes
    font_family: str = "Outfit"
    font_size: int = 11
