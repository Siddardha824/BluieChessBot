from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ThemePreset:
    name: str

    board_light: str
    board_dark: str

    move_highlight: str
    selected_square: str

    arrow_color: str

    eval_positive: str
    eval_negative: str

    coord_light: Optional[str] = None
    coord_dark: Optional[str] = None