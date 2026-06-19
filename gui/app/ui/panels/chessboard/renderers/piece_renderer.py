from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
from typing import TYPE_CHECKING, Dict
from gui.app.shared import SPRITE_SHEET
from gui.utils import get_logger
from gui.app.board.services.board_mapper import BoardMapper

if TYPE_CHECKING:
    from ..models.board_geometry import BoardGeometry
    from gui.app.board.models.board_state import BoardState

logger = get_logger(__name__)

class PieceRenderer:
    def __init__(self, geometry: "BoardGeometry"):
        """
        Initializes the PieceRenderer, loads the spritesheet, and slices piece assets.
        
        Args:
            geometry: Reference to the BoardGeometry dataclass.
        """
        self.geometry = geometry
        
        self.piece_order = ('K', 'Q', 'B', 'N', 'R', 'P', 'k', 'q', 'b', 'n', 'r', 'p')
        self.pieces: Dict[str, QPixmap] = {}
        self.scaled_pieces: Dict[str, QPixmap] = {}
        
        self.load_pieces()

    def load_pieces(self) -> None:
        """
        Loads the core spritesheet from path and slices it into individual piece QPixmaps.
        """
        logger.info("Loading piece spritesheet from: %s", SPRITE_SHEET)
        
        if not SPRITE_SHEET.exists():
            logger.error("Spritesheet file not found at: %s", SPRITE_SHEET)
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
            logger.exception("Failed to load or slice piece sprites: %s", e)
            raise

    def update_scaled_pieces(self) -> None:
        """
        Updates scaled piece caches based on the current square size.
        Should be called inside resizeEvent.
        """
        square_size = self.geometry.square_size
        if square_size <= 0:
            return
            
        logger.debug("Scaling pieces to current square size: %sx%s", square_size, square_size)
        
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
            # Map index (0-63, A8-H1) to chess.Square
            sq = BoardMapper.index_to_square(square_idx)
            piece = board_state.view_board.piece_at(sq)
            piece_char = piece.symbol() if piece is not None else '.'
            
            if piece_char != '.':
                rect = self.geometry.square_to_rect(square_idx)
                scaled_pixmap = self.scaled_pieces.get(piece_char)
                
                if scaled_pixmap:
                    painter.drawPixmap(rect.topLeft(), scaled_pixmap)
