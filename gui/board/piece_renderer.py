# gui/board/piece_renderer.py

from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
from typing import TYPE_CHECKING, Dict
from gui.core.config import SPRITE_SHEET
from gui.utils.logger import get_logger

if TYPE_CHECKING:
    from .board_widget import ChessBoard
    from .coordinate_helper import CoordinateHelper
    from gui.models.board_state import BoardState

logger = get_logger(__name__)

class PieceRenderer:
    def __init__(self, board: "ChessBoard", coord_helper: "CoordinateHelper"):
        """
        Initializes the PieceRenderer, loads the spritesheet, and slices piece assets.
        
        Args:
            board: Reference to the parent ChessBoard widget.
            coord_helper: Helper class providing grid square dimensions.
        """
        self.board = board
        self.coord_helper = coord_helper
        
        self.piece_order = ('K', 'Q', 'B', 'N', 'R', 'P', 'k', 'q', 'b', 'n', 'r', 'p')
        self.pieces: Dict[str, QPixmap] = {}
        self.scaled_pieces: Dict[str, QPixmap] = {}
        
        self.load_pieces()

    def load_pieces(self) -> None:
        """
        Loads the core spritesheet from path and slices it into individual piece QPixmaps.
        """
        logger.info(f"Loading piece spritesheet from: {SPRITE_SHEET}")
        
        if not SPRITE_SHEET.exists():
            logger.error(f"Spritesheet file not found at: {SPRITE_SHEET}")
            raise FileNotFoundError(f"Pieces assets file missing: {SPRITE_SHEET}")
            
        try:
            sheet = QPixmap(str(SPRITE_SHEET))
            
            # Spritesheet is composed of 6 columns (pieces) and 2 rows (White first, then Black)
            piece_width = sheet.width() // 6
            piece_height = sheet.height() // 2
            
            index = 0
            for row in range(2):
                for col in range(6):
                    piece_pixmap = sheet.copy(
                        col * piece_width,
                        row * piece_height,
                        piece_width,
                        piece_height
                    )
                    piece_char = self.piece_order[index]
                    self.pieces[piece_char] = piece_pixmap
                    self.scaled_pieces[piece_char] = piece_pixmap
                    index += 1
                    
            logger.info("Successfully loaded and sliced all 12 piece sprites.")
        except Exception as e:
            logger.exception(f"Failed to load or slice piece sprites: {e}")
            raise

    def update_scaled_pieces(self) -> None:
        """
        Updates scaled piece caches based on the current square size.
        Should be called inside resizeEvent.
        """
        square_size = self.coord_helper.square_size
        if square_size <= 0:
            return
            
        logger.debug(f"Scaling pieces to current square size: {square_size}x{square_size}")
        
        for piece_char, pixmap in self.pieces.items():
            self.scaled_pieces[piece_char] = pixmap.scaled(
                square_size,
                square_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

    def draw_pieces(self, painter: QPainter, board_state: "BoardState") -> None:
        """
        Iterates over the 64 squares of the board and paints active pieces at their rect positions.
        """
        for square_idx in range(64):
            piece_char = board_state.piece_at(square_idx)
            
            if piece_char != '.':
                rect = self.coord_helper.square_to_rect(square_idx)
                scaled_pixmap = self.scaled_pieces.get(piece_char)
                
                if scaled_pixmap:
                    painter.drawPixmap(rect.topLeft(), scaled_pixmap)
