import tkinter as tk
from core.config import ASSETS_DIR
from board.renderer import BoardRenderer
from board.pieces import STARTING_POSITION
from board.sprite_manager import SpriteManager
from board.piece_renderer import PieceRenderer
from board.render_context import RenderContext

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

        self.selected_square = None

        self.board_state = STARTING_POSITION
        self.sprite_manager = SpriteManager(ASSETS_DIR / "Pieces.png")

        self.piece_renderer = PieceRenderer(self, self.sprite_manager)
        self.renderer = BoardRenderer(self, theme, self.piece_renderer)

        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)

        self.draw()

    def on_resize(self, event):
        canvas_size = min(event.width, event.height)

        self.padding = canvas_size * 0.05

        self.board_size = canvas_size - (self.padding * 2)

        self.tile_size = self.board_size / 8

        self.origin = ((event.width - self.board_size) / 2, (event.height - self.board_size) / 2)

        self.draw()

    def on_click(self, event):
        mouse_x = event.x
        mouse_y = event.y

        origin_x, origin_y = self.origin

        board_x = mouse_x - origin_x
        board_y = mouse_y - origin_y

        if board_x < 0 or board_y < 0:
            return

        col = int(board_x // self.tile_size)
        row = int(board_y // self.tile_size)

        if row < 0 or row > 7:
            return

        if col < 0 or col > 7:
            return

        self.selected_square = (row, col)

        self.draw()

    def draw(self):

        context = RenderContext(
            tile_size=self.tile_size,
            origin_x=self.origin[0],
            origin_y=self.origin[1],
            board_state=self.board_state,
            selected_square=self.selected_square
        )

        self.renderer.draw(context)
