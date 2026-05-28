# gui/themes/colors.py

from PySide6.QtGui import QColor

# ==========================================
# 1. CLASSIC LICHESS BLUE/GREY THEME COLORS
# ==========================================
LICHESS_LIGHT_HEX = "#EFEFED"
LICHESS_DARK_HEX = "#70A2CA"

LIGHT_SQUARE = QColor(LICHESS_LIGHT_HEX)
DARK_SQUARE = QColor(LICHESS_DARK_HEX)

# Coordinate label text color
TEXT_LIGHT_SQUARE = QColor("#70A2CA")
TEXT_DARK_SQUARE = QColor("#EFEFED")

# Semi-transparent overlays
SELECTION_COLOR = QColor(247, 247, 105, 130)
LEGAL_MOVE_COLOR = QColor(25, 45, 65, 120)
LAST_MOVE_COLOR = QColor(255, 255, 150, 100)
CHECK_COLOR = QColor(240, 80, 80, 140)

# Panel UI
PANEL_BG = QColor("#1E1E1E")
PANEL_TEXT = QColor("#D4D4D4")
PANEL_TEXT_MUTED = QColor("#888888")
PANEL_BORDER = QColor("#3F3F3F")

# Console log streams
CONSOLE_IN = QColor("#4FC1FF")
CONSOLE_OUT = QColor("#9CDCFE")
CONSOLE_INFO = QColor("#B5CEA8")
CONSOLE_ERROR = QColor("#F44336")

# Evaluation bar
EVAL_WHITE = QColor("#EFEFED")
EVAL_BLACK = QColor("#313131")


# ==========================================
# 2. SIGNATURE BLUIE QUANTUM THEME COLORS
# ==========================================
QUANTUM_LIGHT_SQUARE = QColor("#D8D2EC")          # Lavender Space Dust
QUANTUM_DARK_SQUARE = QColor("#2B1D61")           # Quantum Indigo/Violet

# Highlights
QUANTUM_SELECTION = QColor(0, 229, 255, 120)      # Neon Cyan selection pulse
QUANTUM_LEGAL_MOVE = QColor(0, 229, 255, 100)     # Neon Cyan legal moves
QUANTUM_LAST_MOVE = QColor(124, 77, 255, 90)      # Translucent purple
QUANTUM_CHECK = QColor(255, 64, 129, 140)         # Cosmic Pink check alert

# Text Coordinates
QUANTUM_TEXT_LIGHT = QColor("#2B1D61")
QUANTUM_TEXT_DARK = QColor("#D8D2EC")

# Panel UI
QUANTUM_PANEL_BG = QColor("#0B0813")              # Deep dark space obsidian
QUANTUM_PANEL_TEXT = QColor("#E0F7FA")            # Arctic Silver text
QUANTUM_PANEL_TEXT_MUTED = QColor("#78909C")      # Cool slate gray
QUANTUM_PANEL_BORDER = QColor("#00E5FF")          # Cybernetic Neon Cyan

# Console streams
QUANTUM_CONSOLE_IN = QColor("#00E5FF")
QUANTUM_CONSOLE_OUT = QColor("#E040FB")           # Electric Fuchsia
QUANTUM_CONSOLE_INFO = QColor("#B2FF59")          # High-voltage Lime
QUANTUM_CONSOLE_ERROR = QColor("#FF1744")         # Hot Neon Red

# Evaluation bar
QUANTUM_EVAL_WHITE = QColor("#D8D2EC")
QUANTUM_EVAL_BLACK = QColor("#120E22")


# ==========================================
# 3. CLASSIC FOREST GREEN THEME COLORS
# ==========================================
GREEN_LIGHT_SQUARE = QColor("#FFFFDD")
GREEN_DARK_SQUARE = QColor("#86A666")

# Highlights
GREEN_SELECTION = QColor(247, 247, 105, 130)
GREEN_LEGAL_MOVE = QColor(50, 80, 40, 120)
GREEN_LAST_MOVE = QColor(255, 255, 150, 100)
GREEN_CHECK = QColor(240, 80, 80, 140)

# Text Coordinates
GREEN_TEXT_LIGHT = QColor("#86A666")
GREEN_TEXT_DARK = QColor("#FFFFDD")

# Panel UI
GREEN_PANEL_BG = QColor("#1C2321")
GREEN_PANEL_TEXT = QColor("#D8F3DC")
GREEN_PANEL_TEXT_MUTED = QColor("#74C69D")
GREEN_PANEL_BORDER = QColor("#2D6A4F")

# Console streams
GREEN_CONSOLE_IN = QColor("#74C69D")
GREEN_CONSOLE_OUT = QColor("#95D5B2")
GREEN_CONSOLE_INFO = QColor("#D8F3DC")
GREEN_CONSOLE_ERROR = QColor("#FF87AB")

# Evaluation bar
GREEN_EVAL_WHITE = QColor("#FFFFDD")
GREEN_EVAL_BLACK = QColor("#1B4332")
