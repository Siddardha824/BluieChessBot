import chess
from gui.app.board.services.board_mapper import BoardMapper
from gui.utils import get_logger

logger = get_logger(__name__)

class InteractionManager:
    def __init__(self, app_manager, highlight_manager, update_callback):
        """
        Initializes the InteractionManager.
        
        Args:
            app_manager: Central AppManager instance.
            highlight_manager: HighlightManager instance.
            update_callback: Callback function to trigger UI updates (repaints).
        """
        self._manager = app_manager
        self.highlight_manager = highlight_manager
        self.update_callback = update_callback

    def handle_square_click(self, square_idx: int) -> None:
        """
        Processes click events on board squares based on active states.
        """
        board_state = self._manager.board.session.view_board  # underlying chess.Board
        piece = board_state.piece_at(BoardMapper.index_to_square(square_idx))
        selected_idx = self.highlight_manager.selected_square
        
        logger.debug("Click on square %s. Active selection: %s", square_idx, selected_idx)

        # --- Case A: No square is currently selected ---
        if selected_idx is None:
            if piece is None:
                return
                
            # Check if clicked piece matches the color of the current turn
            if piece.color != board_state.turn:
                logger.debug("Ignored click: not side to move's piece.")
                return
                
            # Select the piece and cache legal destinations
            sq = BoardMapper.index_to_square(square_idx)
            legal_dests = []
            for move in board_state.legal_moves:
                if move.from_square == sq:
                    dest_idx = BoardMapper.coord_to_index(chess.square_name(move.to_square))
                    legal_dests.append(dest_idx)
                    
            self.highlight_manager.select_square(square_idx, legal_dests)
            self.update_callback()
            
        # --- Case B: A square is already selected ---
        else:
            # B1. Clicking the exact same square deselects it
            if square_idx == selected_idx:
                self.highlight_manager.clear_selection()
                self.update_callback()
                return

            # B2. Clicking a legal target square executes the move
            if square_idx in self.highlight_manager.legal_moves:
                from_sq = BoardMapper.index_to_square(selected_idx)
                to_sq = BoardMapper.index_to_square(square_idx)
                
                # Check for pawn promotion (if pawn moves to rank 8 or 1)
                move = chess.Move(from_sq, to_sq)
                piece_type = board_state.piece_type_at(from_sq)
                if piece_type == chess.PAWN:
                    to_rank = chess.square_rank(to_sq)
                    if to_rank == 7 or to_rank == 0:
                        move.promotion = chess.QUEEN
                
                success = self._manager.board.make_move(move.uci())
                
                if success:
                    logger.info("Executed move: %s", move.uci())
                    self.highlight_manager.clear_selection()
                    self.update_callback()
                else:
                    logger.warning("Move execution failed: %s", move.uci())
                    
            # B3. Clicking another piece of the current active side switches selection directly
            elif piece is not None and piece.color == board_state.turn:
                logger.debug("Switching selection to square %s", square_idx)
                sq = BoardMapper.index_to_square(square_idx)
                legal_dests = []
                for move in board_state.legal_moves:
                    if move.from_square == sq:
                        dest_idx = BoardMapper.coord_to_index(chess.square_name(move.to_square))
                        legal_dests.append(dest_idx)
                        
                self.highlight_manager.select_square(square_idx, legal_dests)
                self.update_callback()
                
            # B4. Clicking anywhere else (illegal move / empty square) cancels selection
            else:
                self.highlight_manager.clear_selection()
                self.update_callback()
