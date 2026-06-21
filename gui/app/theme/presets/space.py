from ..models.theme_preset import ThemePreset

SPACE_THEME = ThemePreset(
    name="space",

    board_light="#314674",      # Deep space nebula blue
    board_dark="#0c1225",       # Cosmos dark blue/black

    move_highlight="#ff9100",   # Vibrant orange highlight for last move
    selected_square="#ff3d00",  # Neon red/orange highlight for selected square

    arrow_color="#ffab40",      # Bright neon orange for engine arrows

    eval_positive="#4caf50",
    eval_negative="#e53935",

    coord_light="#ff9100",      # Orange coordinates on dark squares
    coord_dark="#ff3d00"        # Red coordinates on light squares
)