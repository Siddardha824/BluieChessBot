class BoardController:
    def __init__(self, game_state, ui_state):

        self.game_state = game_state
        self.ui_state = ui_state

    def handle_square_clicks(self, square) :
        # If there is no selection, select the current square and return
        if self.ui_state.selected_square is None:
            self.ui_state.selected_square = square
            return

        # Deselect if clicking the already selected square
        if self.ui_state.selected_square == square:
            self.ui_state.selected_square = None
            return

        # If the selected square is different from the already selected square
        start_square = self.ui_state.selected_square

        start_row, start_col = start_square

        if self.game_state.board[start_row][start_col] != " ":
            self.game_state.make_move((start_row, start_col), square)
        
        self.ui_state.selected_square = None