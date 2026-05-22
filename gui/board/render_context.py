class RenderContext:

    def __init__(
        self,
        tile_size,
        origin_x,
        origin_y,
        board_state,
        selected_square
    ):

        self.tile_size = tile_size

        self.origin_x = origin_x
        self.origin_y = origin_y

        self.board_state = board_state

        self.selected_square = selected_square