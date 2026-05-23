class BoardController:
    def __init__(self, chessboard, game_state, ui_state):

        self.chessboard = chessboard
        self.game_state = game_state
        self.ui_state = ui_state

    def on_resize(self, event):
        canvas_size = min(event.width, event.height)

        self.chessboard.padding = canvas_size * 0.05

        self.chessboard.board_size = canvas_size - (self.chessboard.padding * 2)

        self.chessboard.tile_size = self.chessboard.board_size / 8

        self.chessboard.origin = ((event.width - self.chessboard.board_size) / 2, (event.height - self.chessboard.board_size) / 2)

        self.chessboard.draw()
    
    def handle_mouse_press(self, event):
        square = self.chessboard.screen_to_square(event.x, event.y)

        if square is None:
            return
        
        row, col = square

        piece = self.game_state.board[row][col]

        if piece == " ":
            return

        self.ui_state.dragging_square = square
        self.ui_state.dragging_piece = piece
        self.ui_state.drag_position = (event.x, event.y)

        self.chessboard.draw()

    def handle_mouse_drag(self, event):

        if self.ui_state.dragging_piece is None:
            return

        self.ui_state.drag_position = (event.x, event.y)

        self.chessboard.draw()

    def handle_mouse_release(self, event):

        if self.ui_state.dragging_square is None:
            return

        target_square = self.chessboard.screen_to_square(event.x, event.y)
        start_square = self.ui_state.dragging_square

        if target_square is not None and target_square != start_square:

            self.game_state.make_move(
                start_square,
                target_square
            )

        self.ui_state.dragging_square = None
        self.ui_state.dragging_piece = None

        self.chessboard.draw()

