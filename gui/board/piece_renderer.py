class PieceRenderer:
    def __init__(self, canvas, sprite_manager):

        self.canvas = canvas
        self.sprite_manager = sprite_manager

    def draw_pieces(self, context):
        for row in range(8):
            for col in range(8):
                piece = context.board_state[row][col]

                if piece == " ":
                    continue

                image = self.sprite_manager.get_piece_image(piece, context.tile_size)

                x = context.origin_x + col * context.tile_size
                y = context.origin_y + row * context.tile_size

                self.canvas.create_image(x, y, image=image, anchor="nw")