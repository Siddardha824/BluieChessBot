# gui/board/interaction_manager.py

from typing import TYPE_CHECKING
from gui.models.move import Move
from gui.models.pieces import get_color
from gui.utils.logger import get_logger

if TYPE_CHECKING:
    from .board_widget import ChessBoard
    from gui.models.board_state import BoardState
    from .highlights import HighlightManager

logger = get_logger(__name__)

class InteractionManager:
    def __init__(self, board_widget: "ChessBoard", board_state: "BoardState", highlight_manager: "HighlightManager"):
        """
        Initializes the InteractionManager.
        
        Args:
            board_widget: ChessBoard QWidget reference for repaints.
            board_state: Pure data BoardState model.
            highlight_manager: HighlightManager for selection and indicator cache updates.
        """
        self.board_widget = board_widget
        self.board_state = board_state
        self.highlight_manager = highlight_manager

    def handle_square_click(self, square_idx: int) -> None:
        """
        Processes click events on board squares based on active states.
        Supports standard chess interaction flows.
        """
        piece = self.board_state.piece_at(square_idx)
        selected_idx = self.highlight_manager.selected_square
        
        logger.debug(f"Click on square {square_idx} containing '{piece}'. Active selection: {selected_idx}")

        # --- Case A: No square is currently selected ---
        if selected_idx is None:
            # If they click an empty square, ignore
            if piece == '.':
                return
                
            # Check if clicked piece matches the color of the current turn
            piece_color = get_color(piece)
            if piece_color != self.board_state.turn:
                logger.debug("Ignored click: not side to move's piece.")
                return
                
            # Select the piece and cache legal destinations
            legal_destinations = self.board_state.get_legal_moves(square_idx)
            self.highlight_manager.select_square(square_idx, legal_destinations)
            self.board_widget.update()
            
        # --- Case B: A square is already selected ---
        else:
            # B1. Clicking the exact same square deselects it
            if square_idx == selected_idx:
                self.highlight_manager.clear_selection()
                self.board_widget.update()
                return

            # B2. Clicking a legal target square executes the move
            if square_idx in self.highlight_manager.legal_moves:
                move = Move(selected_idx, square_idx)
                success = self.board_state.make_move(move)
                
                if success:
                    logger.info(f"Executed move: {selected_idx} -> {square_idx}")
                    
                    # Update highlighting for last move
                    self.highlight_manager.set_last_move(selected_idx, square_idx)
                    
                    # Check for checks
                    if self.board_state.is_check():
                        # Highlight the active king
                        king_char = 'K' if self.board_state.turn else 'k'
                        for i in range(64):
                            if self.board_state.piece_at(i) == king_char:
                                self.highlight_manager.set_check_square(i)
                                break
                    else:
                        self.highlight_manager.set_check_square(None)
                        
                    # Clear current active selection
                    self.highlight_manager.clear_selection()
                    self.board_widget.update()
                else:
                    logger.warning(f"Move execution failed: {move}")
                    
            # B3. Clicking another piece of the current active side switches selection directly
            elif piece != '.' and get_color(piece) == self.board_state.turn:
                logger.debug(f"Switching selection to square {square_idx}")
                legal_destinations = self.board_state.get_legal_moves(square_idx)
                self.highlight_manager.select_square(square_idx, legal_destinations)
                self.board_widget.update()
                
            # B4. Clicking anywhere else (illegal move / empty square) cancels selection
            else:
                self.highlight_manager.clear_selection()
                self.board_widget.update()
