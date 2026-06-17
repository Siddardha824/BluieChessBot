from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .board_geometry import BoardGeometry
    from gui.app.theme.models.theme_preset import ThemePreset
    from gui.app.board.models.board_state import BoardState
    from .highlights import HighlightManager

@dataclass
class RenderContext:
    geometry: "BoardGeometry"
    theme: "ThemePreset"
    board_state: "BoardState"
    highlight_manager: "HighlightManager"
