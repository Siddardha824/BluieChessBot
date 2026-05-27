# gui/themes/colors.py

from PySide6.QtGui import QColor

# Hex colors for the Classic LiChess Blue/Grey board
LICHESS_LIGHT_HEX = "#EFEFED"
LICHESS_DARK_HEX = "#70A2CA"

# QColor equivalents
LIGHT_SQUARE = QColor(LICHESS_LIGHT_HEX)
DARK_SQUARE = QColor(LICHESS_DARK_HEX)

# Coordinate label text color
TEXT_LIGHT_SQUARE = QColor("#70A2CA")  # Text on light squares uses the dark color
TEXT_DARK_SQUARE = QColor("#EFEFED")   # Text on dark squares uses the light color

# Semi-transparent overlay colors
SELECTION_COLOR = QColor(247, 247, 105, 130)        # Translucent pale tournament yellow overlay
LEGAL_MOVE_COLOR = QColor(25, 45, 65, 120)       # Darker slate-blue semi-transparent indicator
LAST_MOVE_COLOR = QColor(255, 255, 150, 100)        # Warm gold highlight
CHECK_COLOR = QColor(240, 80, 80, 140)              # Bold soft red highlight
