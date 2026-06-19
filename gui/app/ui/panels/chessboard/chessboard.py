import chess
from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QPaintEvent, QResizeEvent, QMouseEvent, QPainter

from ...templates import StyledWidget
from .models import BoardGeometry, HighlightManager, RenderContext
from .renderers import BoardRenderer, CoordinateRenderer, HighlightRenderer, PieceRenderer
from .interaction import InteractionManager

from gui.app.board.services.board_mapper import BoardMapper
from gui.app.game.models.game_state import GameModes
from gui.utils import get_logger

logger = get_logger(__name__)

class Chessboard(StyledWidget):
    """
        Acts as a pure UI container that delegates mouse clicks to InteractionManager,
        size-recalculations to BoardGeometry, and drawing pipelines to specialized renderers.
    """

    def __init__(self, app_manager, parent=None):
        """
        Initializes the interactive ChessBoard QWidget workspace frame.
        """
        super().__init__("chessboard", parent)
        self.setMinimumSize(400, 400)
        
        self._manager = app_manager
        
        # 1. Models
        self.board_geometry = BoardGeometry()
        self.highlight_manager = HighlightManager()
        
        # 2. Interaction Manager
        self.interaction_manager = InteractionManager(
            app_manager=self._manager,
            highlight_manager=self.highlight_manager,
            update_callback=self.update
        )
        
        # 3. Renderers
        self.board_renderer = BoardRenderer()
        self.coord_renderer = CoordinateRenderer()
        self.highlight_renderer = HighlightRenderer()
        self.piece_renderer = PieceRenderer(self.board_geometry)
        
        # Connect to theme, position changes, game over, and mode changes
        self._manager.theme.theme_changed.connect(self.on_theme_changed)
        self._manager.board.position_changed.connect(self.on_position_changed)
        self._manager.game.game_over.connect(self.on_game_over)
        self._manager.game.state.game_mode_changed.connect(self.on_game_mode_changed)
        
        logger.info("Pure UI Chessboard widget successfully initialized.")

    def sizeHint(self) -> QSize:
        """Suggests a standard layout starting size."""
        return QSize(640, 640)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Triggered when the board widget undergoes window resizing.
        Updates board geometry offsets and dimensions.
        """
        logger.debug("Resizing Chessboard: updating geometry calculations.")
        self.board_geometry.update(self.width(), self.height())
        self.piece_renderer.update_scaled_pieces()
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Executes board painting pipeline.
        """
        board_state = self._manager.board.getSession
        theme_preset = self._manager.theme.preset
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Assemble active context frame
        context = RenderContext(
            geometry=self.board_geometry,
            theme=theme_preset,
            board_state=board_state,
            highlight_manager=self.highlight_manager
        )
        
        # Render layers sequentially
        self.board_renderer.draw(painter, context)
        self.coord_renderer.draw(painter, context)
        self.highlight_renderer.draw(painter, context)
        self.piece_renderer.draw_pieces(painter, board_state)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Maps clicked screen coordinates to a chess board square index 
        and routes it to the InteractionManager.
        """
        square = self.board_geometry.pixel_to_square(event.position())
        if square is not None:
            logger.debug("Chessboard mousePress: mapped to square index %s", square)
            self.interaction_manager.handle_square_click(square)
        super().mousePressEvent(event)

    def on_theme_changed(self, theme_name: str) -> None:
        """Triggered when the application theme changes."""
        logger.debug("Chessboard notified of theme change: %s. Repainting.", theme_name)
        self.update()

    def on_position_changed(self, fen: str) -> None:
        """Triggered when the board position is updated."""
        logger.debug("Chessboard notified of position change. Repainting.")
        board_session = self._manager.board.getSession
        board_state = board_session.getBoard
        
        # Clear game over badges when a new position is loaded/played,
        # unless the position itself is a game-over state.
        if not board_state.is_game_over():
            self.highlight_manager.game_over_result = None
            self.highlight_manager.game_over_reason = None
        
        if not board_session.move_stack:
            self.highlight_manager.reset()
        else:
            last_move = board_session.move_stack[-1]
            from_idx = BoardMapper.coord_to_index(chess.square_name(last_move.from_square))
            to_idx = BoardMapper.coord_to_index(chess.square_name(last_move.to_square))
            self.highlight_manager.set_last_move(from_idx, to_idx)
            
        if board_state.is_check():
            king_sq = board_state.king(board_state.turn)
            if king_sq is not None:
                king_idx = BoardMapper.coord_to_index(chess.square_name(king_sq))
                self.highlight_manager.set_check_square(king_idx)
        else:
            self.highlight_manager.set_check_square(None)
        
        self.update()

    def on_game_over(self, result: str, reason: str) -> None:
        """Triggered when the game is over."""
        logger.info("Chessboard notified of game over: %s (%s)", result, reason)
        self.highlight_manager.game_over_result = result
        self.highlight_manager.game_over_reason = reason
        self.update()

    def flip(self) -> None:
        """Flips the visual board perspective."""
        self.board_geometry.flipped = not self.board_geometry.flipped
        self.update()

    def on_game_mode_changed(self, mode: GameModes) -> None:
        """Triggered when the game mode changes."""
        logger.info("Chessboard notified of mode change: %s", mode.name)
        if mode == GameModes.PLAY_BLACK:
            self.board_geometry.flipped = True
        else:
            self.board_geometry.flipped = False
        self.update()
