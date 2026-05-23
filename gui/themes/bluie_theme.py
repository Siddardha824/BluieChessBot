from themes.base_theme import BaseTheme


class BluieTheme(BaseTheme):
    WINDOW_BG = "#0B132B"  # Deep space midnight blue background

    LIGHT_SQUARE = "#DBEAFE"  # Cool ice blue light squares
    DARK_SQUARE = "#4051CF"   # Electric cobalt dark squares

    HIGHLIGHT = "#38BDF8"  # Energetic neon sky-blue accents

    BORDER = "#1C2541"  # Midnight blue card borders

    TEXT = "#F8FAFC"  # Frosted slate white text

    # Dashboard & Control Panel specific theme customization overrides
    CARD_BG = "#1C2541"   # Sleek dark navy card backgrounds
    INPUT_BG = "#0F172A"  # Dark slate blue for console logs & textboxes
    SUCCESS = "#10B981"   # Emerald green connection indicator
    DANGER = "#F43F5E"    # Vibrant coral rose for error/disconnect buttons
    WARNING = "#F59E0B"   # Rich golden amber for notice alerts