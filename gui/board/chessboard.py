import tkinter as tk

from core.config import ASSETS_DIR

from board.renderer import BoardRenderer
from board.sprite_manager import SpriteManager
from board.piece_renderer import PieceRenderer
from board.render_context import RenderContext
from board.board_controller import BoardController

from state.game_state import GameState
from state.ui_state import UIState

class ChessBoard(tk.Canvas):

    def __init__(self, parent, theme):
        super().__init__(
            parent,
            bg=theme.WINDOW_BG,
            highlightthickness=0
        )

        self.theme = theme

        self.tile_size = 64
        self.padding = 20
        self.origin = (self.padding, self.padding)

        self.game_state = GameState()
        self.ui_state = UIState()

        self.board_controller = BoardController(self.game_state, self.ui_state)
        
        self.sprite_manager = SpriteManager(ASSETS_DIR / "Pieces.png")

        self.piece_renderer = PieceRenderer(self, self.sprite_manager)
        self.renderer = BoardRenderer(self, theme, self.piece_renderer)

        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_mouse_press)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)

        self.draw()

    def on_resize(self, event):
        canvas_size = min(event.width, event.height)

        self.padding = canvas_size * 0.05

        self.board_size = canvas_size - (self.padding * 2)

        self.tile_size = self.board_size / 8

        self.origin = ((event.width - self.board_size) / 2, (event.height - self.board_size) / 2)

        self.draw()
    
    def screen_to_square(self, x, y):

        origin_x, origin_y = self.origin

        board_x = x - origin_x
        board_y = y - origin_y

        if board_x < 0 or board_y < 0:
            return None

        col = int(board_x // self.tile_size)
        row = int(board_y // self.tile_size)

        if not (0 <= row < 8 and 0 <= col < 8):
            return None

        return (row, col)

    def on_click(self, event):
        square = self.screen_to_square(event.x, event.y)

        if square is None:
            return
        
        self.board_controller.handle_square_clicks(square=square)
        self.draw()

    def on_mouse_press(self, event):
        square = self.screen_to_square(event.x, event.y)

        if square is None:
            return
        
        row, col = square

        piece = self.game_state.board[row][col]

        if piece == " ":
            return

        self.ui_state.dragging_square = square
        self.ui_state.dragging_piece = piece
        self.ui_state.drag_position = (event.x, event.y)

        self.draw()

    def on_mouse_drag(self, event):

        if self.ui_state.dragging_piece is None:
            return

        self.ui_state.drag_position = (event.x, event.y)

        self.draw()

    def on_mouse_release(self, event):

        if self.ui_state.dragging_square is None:
            return

        target_square = self.screen_to_square(event.x, event.y)
        start_square = self.ui_state.dragging_square

        if target_square is not None and target_square != start_square:

            self.game_state.make_move(
                start_square,
                target_square
            )

        self.ui_state.dragging_square = None
        self.ui_state.dragging_piece = None

        self.draw()

    def draw(self):

        context = RenderContext(
            tile_size=self.tile_size,
            origin_x=self.origin[0],
            origin_y=self.origin[1],
            board_state=self.game_state.board,
            selected_square=self.ui_state.selected_square,
            dragging_square=self.ui_state.dragging_square,
            dragging_piece=self.ui_state.dragging_piece,
            drag_position=self.ui_state.drag_position
        )

        self.renderer.draw(context)
