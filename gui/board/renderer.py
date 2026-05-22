class BoardRenderer:

    def __init__(self, canvas, theme, piece_renderer):

        self.canvas = canvas
        self.theme = theme
        self.piece_renderer = piece_renderer

    def draw(self, context):

        self.canvas.delete("all")

        self.draw_background()

        self.draw_squares(context)

        self.draw_coordinates(context)

        self.draw_selected_square(context)

        self.piece_renderer.draw_pieces(context)

    def draw_background(self):
        self.canvas.configure(bg=self.theme.WINDOW_BG)

    def draw_squares(self, context):
        for row in range(8):
            for col in range(8):
                x1 = context.origin_x + col * context.tile_size
                y1 = context.origin_y + row * context.tile_size

                x2 = x1 + context.tile_size
                y2 = y1 + context.tile_size

                color = (
                    self.theme.LIGHT_SQUARE
                    if (row + col) % 2 == 0
                    else self.theme.DARK_SQUARE
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline=""
                )

    def draw_coordinates(self, context):
        origin_x = context.origin_x
        origin_y = context.origin_y
        tile_size = context.tile_size

        files = "abcdefgh"
        font_size = max(8, int(tile_size * 0.18))

        for col in range(8):
            x = origin_x + col * tile_size + tile_size*0.08
            y = origin_y + 8 * tile_size - tile_size*0.08

            color = (
                self.theme.LIGHT_SQUARE
                if col % 2 == 0
                else self.theme.DARK_SQUARE
            )

            self.canvas.create_text(
                x,
                y,
                text=files[col],
                anchor="sw",
                fill=color,
                font=("Segoe UI", font_size, "bold")
            )

        for row in range(8):
            x = origin_x + tile_size*0.08
            y = origin_y + row * tile_size + tile_size*0.08

            color = (
                self.theme.DARK_SQUARE
                if row % 2 == 0
                else self.theme.LIGHT_SQUARE
            )

            self.canvas.create_text(
                x,
                y,
                text=str(8 - row),
                anchor="nw",
                fill=color,
                font=("Segoe UI", font_size, "bold")
            )

    def draw_selected_square(self, context):
        if context.selected_square is None:
            return
        
        origin_x = context.origin_x
        origin_y = context.origin_y
        tile_size = context.tile_size

        row, col = context.selected_square

        x1 = origin_x + col * tile_size
        y1 = origin_y + row * tile_size
        
        x2 = x1 + tile_size
        y2 = y1 + tile_size

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=self.theme.HIGHLIGHT,
            outline=""
        )


