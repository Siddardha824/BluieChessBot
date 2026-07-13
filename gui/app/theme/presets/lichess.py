from ..models.theme_state import ThemeState

LICHESS_THEME = ThemeState(
    name="lichess",

    bg_window="#262421",

    bg_base="#312e2b",

    bg_panel="#262421",
    border_panel="#3d3935",

    text_primary="#bababa",
    text_secondary="#bababa",
    
    accent_primary="#ffffff",
    accent_secondary="#ffffff",

    status_connected="#FF9800",
    status_disconnected="#9E9E9E",
    status_idle="#2196F3",
    status_searching="#4CAF50",

    board_light="#f0d9b5",
    board_dark="#b58863",

    coord_light="#b58863",
    coord_dark="#f0d9b5",

    move_highlight="#cdd26a",
    selected_square="#7fa650",

    arrow_color="#00ff00",

    eval_positive="#7fa650",
    eval_negative="#cc4444"
)