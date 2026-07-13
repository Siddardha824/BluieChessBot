from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ThemeState:
    name: str

    # Global themes

    # Main Window
    bg_window: str

    # Pages
    bg_base: str

    # Panels
    bg_panel: str
    border_panel: str

    # Text Colors

    # Global Text colors
    text_primary: str
    text_secondary: str

    # Glibal Accent colors
    accent_primary: str
    accent_secondary: str

    # Engine status colors
    status_searching: str
    status_idle: str
    status_connected: str
    status_disconnected: str

    # Chessboard colors

    board_light: str
    board_dark: str

    move_highlight: str
    selected_square: str

    arrow_color: str

    eval_positive: str
    eval_negative: str

    coord_light: str
    coord_dark: str

    @classmethod
    def from_dict(cls, data: dict):
        valid_keys = {f for f in cls.__dataclass_fields__}

        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        return cls(**filtered_data)
