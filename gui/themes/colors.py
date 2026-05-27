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

# Panel/Console Colors
PANEL_BG = QColor("#1E1E1E")                        # Main container panels dark background
PANEL_TEXT = QColor("#D4D4D4")                      # Normal panel text
PANEL_TEXT_MUTED = QColor("#888888")                # Index labels / muted text

# Console Categories text colors
CONSOLE_IN = QColor("#4FC1FF")                      # Cyan for incoming engine signals
CONSOLE_OUT = QColor("#9CDCFE")                     # Light blue for outgoing commands
CONSOLE_INFO = QColor("#B5CEA8")                    # Soft green for info blocks
CONSOLE_ERROR = QColor("#F44336")                   # Bold red for alerts

# Evaluation Bar Colors
EVAL_WHITE = QColor("#EFEFED")                      # Light fill for White's advantage
EVAL_BLACK = QColor("#313131")                      # Dark charcoal fill for Black's advantage

# Border/Divider Colors
PANEL_BORDER = QColor("#3F3F3F")                     # Sleek dark gray border outline for visual segmentation




