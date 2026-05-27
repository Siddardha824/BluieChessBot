# gui/board/board_widget.py

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize
from PySide6.QtGui import QPaintEvent, QResizeEvent, QMouseEvent, QPainter

from gui.models.board_state import BoardState
from gui.themes.default_theme import DefaultTheme
from .coordinate_helper import CoordinateHelper
from .board_renderer import BoardRenderer
from .piece_renderer import PieceRenderer
from .highlights import HighlightManager
from .interaction_manager import InteractionManager
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class ChessBoard(QWidget):
    def __init__(self, parent=None):
        """
        Initializes the interactive ChessBoard QWidget.
        Orchestrates rendering, coordinate mapping, interaction handling, and state storage.
        """
        super().__init__(parent)
        
        self.setMinimumSize(400, 400)
        
        # 1. Initialize Domain State Models & Themes
        self.board_state = BoardState()
        self.theme = DefaultTheme()
        
        # 2. Initialize Helpers & Renderers
        self.coord_helper = CoordinateHelper(self)
        self.board_renderer = BoardRenderer(self, self.coord_helper, self.theme)
        self.piece_renderer = PieceRenderer(self, self.coord_helper)
        
        # 3. Initialize Highlighting & Interaction Controllers
        self.highlight_manager = HighlightManager()
        self.interaction_manager = InteractionManager(self, self.board_state, self.highlight_manager)
        
        logger.info("Decoupled ChessBoard widget successfully initialized.")

    def sizeHint(self) -> QSize:
        """Suggests a standard layout starting size."""
        return QSize(640, 640)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Triggered when the board widget undergoes window resizing.
        Updates board sizing offsets and adjusts/caches scaled piece pixmaps.
        """
        logger.debug("Resizing ChessBoard: updating board geometries.")
        self.coord_helper.update_geometry()
        self.piece_renderer.update_scaled_pieces()
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Executes board painting pipeline.
        Invokes sub-renderers synchronously inside standard event loop frame.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Step A: Draw chess squares and background coordinates
        self.board_renderer.draw_board(painter)
        self.board_renderer.draw_coordinates(painter)
        
        # Step B: Draw active selections, checks, move dots, capture rings, and last moves
        self.board_renderer.draw_highlights(painter, self.highlight_manager, self.board_state)
        
        # Step C: Draw actual chess piece sprites
        self.piece_renderer.draw_pieces(painter, self.board_state)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Maps clicked screen coordinates to a chess board square index 
        and routes the event directly into the InteractionManager.
        """
        # Map pixel to native A8=0 index
        square = self.coord_helper.pixel_to_square(event.position())
        
        if square is not None:
            self.interaction_manager.handle_square_click(square)
        else:
            # Clicked outside active grid: clear selections
            self.highlight_manager.clear_selection()
            self.update()
            
        super().mousePressEvent(event)
