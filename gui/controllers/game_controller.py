# gui/controllers/game_controller.py

from PySide6.QtCore import QObject, Signal
from gui.models.board_state import BoardState
from gui.board.highlights import HighlightManager
from gui.models.move import Move
from gui.models.pieces import get_color
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class GameController(QObject):
    # Signal emitted to notify view widgets that state has changed and a repaint is required
    state_changed = Signal()

    def __init__(self, parent: QObject | None = None):
        """
        Initializes the GameController.
        Owns the primary domain models and interaction states.
        """
        super().__init__(parent)
        self.board_state = BoardState()
        self.highlight_manager = HighlightManager()
        logger.info("GameController successfully initialized and state models allocated.")

    def handle_square_clicked(self, square_idx: int | None) -> None:
        """
        Coordinated slot to handle square selection and move execution.
        Mutates models and emits state_changed signal to request views repaint.
        """
        if square_idx is None:
            logger.debug("GameController clearing selection due to click outside board boundaries.")
            self.highlight_manager.clear_selection()
            self.state_changed.emit()
            return

        piece = self.board_state.piece_at(square_idx)
        selected_idx = self.highlight_manager.selected_square
        
        logger.debug(f"GameController processing click on square {square_idx} containing '{piece}'. Active selection: {selected_idx}")

        # --- Case A: No square is currently selected ---
        if selected_idx is None:
            # Ignore clicks on empty squares
            if piece == '.':
                return
                
            # Restrict selection to pieces matching the active turn's color
            if get_color(piece) != self.board_state.turn:
                logger.debug("GameController ignored click: not the active side to move's piece.")
                return
                
            # Select the piece and cache legal move target squares
            legal_destinations = self.board_state.get_legal_moves(square_idx)
            self.highlight_manager.select_square(square_idx, legal_destinations)
            self.state_changed.emit()
            
        # --- Case B: A square is already selected ---
        else:
            # B1. Clicking the exact same square deselects it
            if square_idx == selected_idx:
                self.highlight_manager.clear_selection()
                self.state_changed.emit()
                return

            # B2. Clicking a legal target square executes the move
            if square_idx in self.highlight_manager.legal_moves:
                move = Move(selected_idx, square_idx)
                success = self.board_state.make_move(move)
                
                if success:
                    logger.info(f"GameController executed move: {selected_idx} -> {square_idx}")
                    
                    # Highlight last move squares
                    self.highlight_manager.set_last_move(selected_idx, square_idx)
                    
                    # Handle check alert highlights
                    if self.board_state.is_check():
                        # Find the active King's square index
                        king_char = 'K' if self.board_state.turn else 'k'
                        for i in range(64):
                            if self.board_state.piece_at(i) == king_char:
                                self.highlight_manager.set_check_square(i)
                                break
                    else:
                        self.highlight_manager.set_check_square(None)
                        
                    # Reset active selection state
                    self.highlight_manager.clear_selection()
                    self.state_changed.emit()
                else:
                    logger.warning(f"GameController failed to execute move: {move}")
                    
            # B3. Clicking another friendly piece of the active side directly switches selection
            elif piece != '.' and get_color(piece) == self.board_state.turn:
                logger.debug(f"GameController switching selection directly to square {square_idx}")
                legal_destinations = self.board_state.get_legal_moves(square_idx)
                self.highlight_manager.select_square(square_idx, legal_destinations)
                self.state_changed.emit()
                
            # B4. Clicking anywhere else (illegal move / empty square) cancels selection
            else:
                logger.debug("GameController clearing selection due to illegal square click.")
                self.highlight_manager.clear_selection()
                self.state_changed.emit()
