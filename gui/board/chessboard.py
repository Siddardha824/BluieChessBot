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

        self.board_controller = BoardController(self, self.game_state, self.ui_state)
        
        self.sprite_manager = SpriteManager(ASSETS_DIR / "Pieces.png")

        self.piece_renderer = PieceRenderer(self, self.sprite_manager)
        self.renderer = BoardRenderer(self, theme, self.piece_renderer)

        self.bind("<Configure>", self.board_controller.on_resize)
        self.bind("<Button-1>", self.board_controller.handle_mouse_press)
        self.bind("<B1-Motion>", self.board_controller.handle_mouse_drag)
        self.bind("<ButtonRelease-1>", self.board_controller.handle_mouse_release)

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
