# gui/board/render_context.py

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .board_geometry import BoardGeometry
    from gui.themes.default_theme import DefaultTheme
    from gui.models.board_state import BoardState
    from .highlights import HighlightManager

@dataclass
class RenderContext:
    geometry: "BoardGeometry"
    theme: "DefaultTheme"
    board_state: "BoardState"
    highlight_manager: "HighlightManager"
