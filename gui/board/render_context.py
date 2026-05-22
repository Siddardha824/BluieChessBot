from dataclasses import dataclass


@dataclass(frozen=True)
class RenderContext:

    tile_size: float

    origin_x: float
    origin_y: float

    board_state: list

    selected_square: tuple | None

    dragging_square: tuple | None

    dragging_piece: str | None

    drag_position: tuple

    @property
    def board_size(self):
        return self.tile_size * 8