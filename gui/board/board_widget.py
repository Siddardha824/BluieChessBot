# gui/board/board_widget.py

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QPaintEvent, QResizeEvent, QMouseEvent, QPainter

from .board_geometry import BoardGeometry
from .coordinate_helper import CoordinateHelper
from .board_renderer import BoardRenderer
from .coordinate_renderer import CoordinateRenderer
from .highlight_renderer import HighlightRenderer
from .piece_renderer import PieceRenderer
from .render_context import RenderContext
from gui.themes import theme_manager, ActiveTheme
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class ChessBoard(QWidget):
    """
    Sleek, interactive, layered custom presentation QWidget for the chessboard canvas.
    
    Implements a highly decoupled rendering architecture separating model data from drawing pipelines.
    Listens for user clicks, maps window pixel points to chess algebraic square indexes, and delegates
    visual representations dynamically to downstream specialized paint layer components (board, coordinates,
    piece textures, overlays).
    """
    # Qt Signal emitted when a mouse press occurs (passes square index or None if clicked outside)
    square_clicked = Signal(object)

    def __init__(self, theme=None, parent=None):
        """
        Initializes the interactive ChessBoard QWidget workspace frame.
        
        Configures geometry helpers and constructs independent decoupled rendering components.
        """
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        
        # 1. State Models (Provided dynamically via Dependency Injection)
        self._board_state = None
        self._highlight_manager = None
        
        # 2. View Geometry & Theme
        self.board_geometry = BoardGeometry()
        self.theme = theme if theme is not None else theme_manager.get_theme()
        self.coord_helper = CoordinateHelper(self)
        
        # 3. Individual decoupled Layer Renderers
        self.board_renderer = BoardRenderer()
        self.coord_renderer = CoordinateRenderer()
        self.highlight_renderer = HighlightRenderer()
        self.piece_renderer = PieceRenderer(self, self.coord_helper)
        
        logger.info("Decoupled BoardWidget successfully initialized.")

    def set_models(self, board_state, highlight_manager) -> None:
        """
        Injects the core data models from the controlling interface.
        """
        self._board_state = board_state
        self._highlight_manager = highlight_manager
        logger.info("Core data models successfully injected into BoardWidget.")

    def sizeHint(self) -> QSize:
        """Suggests a standard layout starting size."""
        return QSize(640, 640)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Triggered when the board widget undergoes window resizing.
        Updates board sizing offsets and updates our geometries dataclass.
        """
        logger.debug("Resizing ChessBoard: updating board geometries.")
        self.coord_helper.update_geometry()
        
        # Mirror current geometries inside our geometry dataclass
        self.board_geometry.board_size = self.coord_helper.board_size
        self.board_geometry.square_size = self.coord_helper.square_size
        self.board_geometry.x_offset = self.coord_helper.x_offset
        self.board_geometry.y_offset = self.coord_helper.y_offset
        
        self.piece_renderer.update_scaled_pieces()
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Executes board painting pipeline using the RenderContext snapshot.
        """
        if self._board_state is None or self._highlight_manager is None:
            logger.warning("ChessBoard paintEvent skipped: State models are not injected yet.")
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Assemble active context frame
        context = RenderContext(
            geometry=self.board_geometry,
            theme=self.theme,
            board_state=self._board_state,
            highlight_manager=self._highlight_manager
        )
        
        # Render layers sequentially
        self.board_renderer.draw(painter, context)
        self.coord_renderer.draw(painter, context)
        self.highlight_renderer.draw(painter, context)
        self.piece_renderer.draw_pieces(painter, self._board_state)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Maps clicked screen coordinates to a chess board square index 
        and emits the square_clicked signal (can be None if clicked outside).
        """
        square = self.coord_helper.pixel_to_square(event.position())
        logger.debug(f"ChessBoard mousePress: mapped to square {square}, emitting signal.")
        self.square_clicked.emit(square)
        super().mousePressEvent(event)

