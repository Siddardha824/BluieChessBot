# gui/controllers/board_controller.py

from PySide6.QtCore import QObject, Signal
from gui.models.board_state import BoardState
from gui.board.highlights import HighlightManager
from gui.models.move import Move
from gui.models.pieces import get_color
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class BoardController(QObject):
    # Public signals to notify the orchestrator or view elements
    state_changed = Signal()
    move_executed = Signal(str)      # Emits SAN notation string on successful moves
    move_undone = Signal()            # Emits when the last move is undone
    game_over = Signal(str)           # Emits a game outcome string when the game ends
    selection_changed = Signal()      # Emits when the active square selection changes

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.board_state = BoardState()
        self.highlight_manager = HighlightManager()

    def _execute_and_register_move(self, move: Move) -> str | None:
        """
        Executes a move on the board, updates highlight markers (last move, checks),
        and emits the move_executed and state_changed signals.
        Returns the SAN move string if successful, None otherwise.
        """
        san_move = self.board_state.make_move(move)
        if san_move is None:
            return None

        # 1. Emit executed move SAN
        self.move_executed.emit(san_move)
        
        # 2. Highlight last move source and destination squares
        self.highlight_manager.set_last_move(move.from_square, move.to_square)
        
        # 3. Handle check alert highlights
        if self.board_state.is_check():
            # Find the active King's square index matching the turn
            king_char = 'K' if self.board_state.turn else 'k'
            for i in range(64):
                if self.board_state.piece_at(i) == king_char:
                    self.highlight_manager.set_check_square(i)
                    break
        else:
            self.highlight_manager.set_check_square(None)
            
        # 4. Trigger views repaint
        self.state_changed.emit()
        self.selection_changed.emit()

        # 5. Check if the played move ended the game
        if self.board_state._board.is_game_over():
            board = self.board_state._board
            if board.is_checkmate():
                winner = "Black" if board.turn else "White"
                outcome = f"Checkmate! {winner} wins."
            elif board.is_stalemate():
                outcome = "Stalemate! The game is a draw."
            elif board.is_insufficient_material():
                outcome = "Draw due to insufficient material."
            elif board.is_fivefold_repetition() or board.is_repetition(3):
                outcome = "Draw due to repetition."
            else:
                outcome = "Game over."
            
            logger.info(f"Game Over detected: {outcome}")
            self.game_over.emit(outcome)

        return san_move

    def handle_square_clicked(self, square_idx: int | None, is_engine_active: bool = False, is_engine_turn: bool = False) -> None:
        """
        Coordinated slot to handle square selection and move execution.
        Mutates models and emits state_changed signal to request views repaint.
        """
        # Protect board clicks: ignore clicks during engine turn or when engine is actively calculating
        if is_engine_turn or is_engine_active:
            logger.debug("BoardController ignoring click: engine operations in progress.")
            return

        if square_idx is None:
            logger.debug("BoardController clearing selection due to click outside board boundaries.")
            self.highlight_manager.clear_selection()
            self.state_changed.emit()
            self.selection_changed.emit()
            return

        piece = self.board_state.piece_at(square_idx)
        selected_idx = self.highlight_manager.selected_square
        
        logger.debug(f"BoardController click on square {square_idx} containing '{piece}'. Selection: {selected_idx}")
        is_overlay_active = self.highlight_manager.debug_overlay_mode.startswith("ATTACKSTO_")

        # --- Case A: No square is currently selected ---
        if selected_idx is None:
            # If debug overlay mode is active, allow selecting empty or opponent squares
            if piece == '.' or get_color(piece) != self.board_state.turn:
                if is_overlay_active:
                    self.highlight_manager.select_square(square_idx, [])
                    self.state_changed.emit()
                    self.selection_changed.emit()
                    return
                else:
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
                self.selection_changed.emit()
                return

            # B2. Clicking a legal target square executes the move
            if square_idx in self.highlight_manager.legal_moves:
                move = Move(selected_idx, square_idx)
                if self._execute_and_register_move(move) is not None:
                    logger.info(f"BoardController executed move: {selected_idx} -> {square_idx}")
                    
                    # Reset active selection state
                    self.highlight_manager.clear_selection()
                    self.state_changed.emit()
            
            # B3. Clicking another friendly piece of the active side directly switches selection
            elif piece != '.' and get_color(piece) == self.board_state.turn:
                logger.debug(f"BoardController switching selection directly to square {square_idx}")
                legal_destinations = self.board_state.get_legal_moves(square_idx)
                self.highlight_manager.select_square(square_idx, legal_destinations)
                self.state_changed.emit()
                
            # B4. Clicking anywhere else (illegal move / empty square) cancels selection or switches for debug
            else:
                if is_overlay_active:
                    logger.debug(f"BoardController switching selection directly to square {square_idx} for debug threats")
                    self.highlight_manager.select_square(square_idx, [])
                    self.state_changed.emit()
                else:
                    logger.debug("BoardController clearing selection due to illegal square click.")
                    self.highlight_manager.clear_selection()
                    self.state_changed.emit()
        self.selection_changed.emit()

    def undo_last_move(self) -> None:
        """
        Undoes the last move played on the board, updates highlight states,
        emits the move_undone signal, and repaints the board.
        """
        popped = self.board_state.undo_last_move()
        if popped is not None:
            # 1. Update last move highlights from the new top of the stack
            if len(self.board_state._board.move_stack) > 0:
                last_move = self.board_state._board.move_stack[-1]
                from_cpp = self.board_state._convert_square(last_move.from_square)
                to_cpp = self.board_state._convert_square(last_move.to_square)
                self.highlight_manager.set_last_move(from_cpp, to_cpp)
            else:
                self.highlight_manager.set_last_move(None, None)
                
            # 2. Reset check highlights
            if self.board_state.is_check():
                king_char = 'K' if self.board_state.turn else 'k'
                for i in range(64):
                    if self.board_state.piece_at(i) == king_char:
                        self.highlight_manager.set_check_square(i)
                        break
            else:
                self.highlight_manager.set_check_square(None)
                
            # 3. Clear active selection highlights
            self.highlight_manager.clear_selection()
            
            # 4. Emit signal to update Move List Widget
            self.move_undone.emit()
            
            # 5. Trigger views repaint
            self.state_changed.emit()
            self.selection_changed.emit()
            logger.info("Successfully undone the last played move.")
