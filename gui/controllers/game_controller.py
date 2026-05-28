# gui/controllers/game_controller.py

import os
from PySide6.QtCore import QObject, Signal, QTimer
from gui.models.board_state import BoardState
from gui.board.highlights import HighlightManager
from gui.models.move import Move
from gui.models.pieces import get_color
from gui.engine.engine_manager import EngineManager
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class GameControllerSignals(QObject):
    """
    Decoupled lightweight QObject container dedicated strictly to managing
    PySide6 signal allocations. Isulates Qt meta-object bindings from the
    pure Python GameController.
    """
    state_changed = Signal()
    move_executed = Signal(str)  # Emits SAN notation string on successful moves
    move_undone = Signal()  # Emits when the last move is popped/undone

class GameController:
    def __init__(self, parent: QObject | None = None):
        """
        Initializes the GameController.
        Converts GameController to a pure Python class to protect all logic,
        mathematics, and turn evaluation helpers from Shiboken C++ marshalling errors.
        """
        # 1. Instantiate the signals container
        self.signals = GameControllerSignals()
        
        self.board_state = BoardState()
        self.highlight_manager = HighlightManager()
        
        # 2. Instantiate the EngineManager, using the signals QObject as the Qt parent context
        self.engine_manager = EngineManager(self.signals)
        self.engine_mode = "play_black"  # Modes: "play_black", "play_white", "free_analysis", "two_human"
        
        # 3. Automatically resolve compiled C++ engine executable path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        self.engine_path = os.path.join(project_root, "build", "BluieChessBot.exe")
        
        # 4. Connect engine signals directly to Python slot methods using safe lambdas
        self.engine_manager.bestmove_received.connect(lambda move: self.handle_engine_best_move(move))
        self.engine_manager.debug_overlay_received.connect(
            lambda otype, hex_bb: self.handle_debug_overlay_received(otype, hex_bb)
        )
        
        # 5. Start the engine process automatically on bootstrap
        if os.path.exists(self.engine_path):
            self.engine_manager.start_engine(self.engine_path)
        else:
            logger.warning(f"Engine executable not found at startup: {self.engine_path}. Awaiting manual launch.")
            
        logger.info("GameController successfully initialized and engine process started.")

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
        self.signals.move_executed.emit(san_move)
        
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
        self.signals.state_changed.emit()
        self.query_active_debug_overlay()
        return san_move

    def handle_square_clicked(self, square_idx: int | None) -> None:
        """
        Coordinated slot to handle square selection and move execution.
        Mutates models and emits state_changed signal to request views repaint.
        """
        # Protect board clicks: ignore clicks during engine turn or when engine is active
        if self.is_engine_turn() or self.engine_manager.engine_status == "Searching":
            logger.debug("GameController ignoring human click: engine turn in progress.")
            return

        if square_idx is None:
            logger.debug("GameController clearing selection due to click outside board boundaries.")
            self.highlight_manager.clear_selection()
            self.signals.state_changed.emit()
            self.query_active_debug_overlay()
            return

        piece = self.board_state.piece_at(square_idx)
        selected_idx = self.highlight_manager.selected_square
        
        logger.debug(f"GameController processing click on square {square_idx} containing '{piece}'. Active selection: {selected_idx}")

        is_overlay_active = self.highlight_manager.debug_overlay_mode.startswith("ATTACKSTO_")

        # --- Case A: No square is currently selected ---
        if selected_idx is None:
            # If debug overlay mode is active, allow selecting empty or opponent squares
            if piece == '.' or get_color(piece) != self.board_state.turn:
                if is_overlay_active:
                    self.highlight_manager.select_square(square_idx, [])
                    self.signals.state_changed.emit()
                    self.query_active_debug_overlay()
                    return
                else:
                    return
                
            # Select the piece and cache legal move target squares
            legal_destinations = self.board_state.get_legal_moves(square_idx)
            self.highlight_manager.select_square(square_idx, legal_destinations)
            self.signals.state_changed.emit()
            
        # --- Case B: A square is already selected ---
        else:
            # B1. Clicking the exact same square deselects it
            if square_idx == selected_idx:
                self.highlight_manager.clear_selection()
                self.signals.state_changed.emit()
                self.query_active_debug_overlay()
                return

            # B2. Clicking a legal target square executes the move
            if square_idx in self.highlight_manager.legal_moves:
                move = Move(selected_idx, square_idx)
                if self._execute_and_register_move(move) is not None:
                    logger.info(f"GameController executed move: {selected_idx} -> {square_idx}")
                    
                    # Reset active selection state
                    self.highlight_manager.clear_selection()
                    self.signals.state_changed.emit()
                    
                    # --- Play Loop: Check if it's the engine's turn to respond ---
                    if self.is_engine_turn():
                        # Use a single-shot timer to let the GUI paint the human's move first!
                        QTimer.singleShot(150, self.trigger_engine_move)
                else:
                    logger.warning(f"GameController failed to execute move: {move}")
                    
            # B3. Clicking another friendly piece of the active side directly switches selection
            elif piece != '.' and get_color(piece) == self.board_state.turn:
                logger.debug(f"GameController switching selection directly to square {square_idx}")
                legal_destinations = self.board_state.get_legal_moves(square_idx)
                self.highlight_manager.select_square(square_idx, legal_destinations)
                self.signals.state_changed.emit()
                
            # B4. Clicking anywhere else (illegal move / empty square) cancels selection or switches for debug
            else:
                if is_overlay_active:
                    logger.debug(f"GameController switching selection directly to square {square_idx} for debug threats")
                    self.highlight_manager.select_square(square_idx, [])
                    self.signals.state_changed.emit()
                else:
                    logger.debug("GameController clearing selection due to illegal square click.")
                    self.highlight_manager.clear_selection()
                    self.signals.state_changed.emit()
        self.query_active_debug_overlay()

    def is_engine_turn(self) -> bool:
        """
        Determines if it is currently the engine's turn to play based on engine_mode configuration.
        """
        if self.engine_mode == "play_black" and not self.board_state.turn:
            return True
        if self.engine_mode == "play_white" and self.board_state.turn:
            return True
        return False

    def trigger_engine_move(self) -> None:
        """
        Submits current FEN position and starts search to let engine play.
        """
        if not self.is_engine_turn():
            return
            
        logger.info("Triggering background engine search...")
        fen = self.board_state.get_fen()
        self.engine_manager.send_position(fen)
        self.engine_manager.start_search(depth=10)

    def handle_engine_best_move(self, move_str: str) -> None:
        """
        Slot responding to engine's calculation completion. Parses coordinate
        algebraic move representation and executes it on board models.
        """
        if not self.is_engine_turn():
            return
            
        logger.info(f"Engine played move: {move_str}")
        try:
            move = Move.from_uci(move_str)
            if self._execute_and_register_move(move) is not None:
                # Reset active selection state just in case
                self.highlight_manager.clear_selection()
                self.signals.state_changed.emit()
            else:
                logger.error(f"Engine calculated an illegal move: {move_str}. Undoing human's last move to unfreeze play...")
                self.undo_last_move()
        except Exception as e:
            logger.error(f"Failed to play engine calculated move '{move_str}': {e}", exc_info=True)

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
            self.signals.move_undone.emit()
            
            # 5. Trigger views repaint
            self.signals.state_changed.emit()
            self.query_active_debug_overlay()
            logger.info("Successfully undone the last played move.")

    def set_debug_overlay_mode(self, mode: str) -> None:
        """Sets the active debug overlay mode and triggers query."""
        self.highlight_manager.debug_overlay_mode = mode
        self.query_active_debug_overlay()

    def query_active_debug_overlay(self) -> None:
        """Sends the appropriate uci debug command to request threat overlays."""
        mode = self.highlight_manager.debug_overlay_mode
        if mode == "NONE":
            self.highlight_manager.debug_overlay_squares = []
            self.signals.state_changed.emit()
            return
            
        fen = self.board_state.get_fen()
        
        # Sync board position to engine
        self.engine_manager.send_position(fen)
        
        if mode == "WHITE_ATTACKS":
            self.engine_manager.send_command("bluie-debug attacks white")
        elif mode == "BLACK_ATTACKS":
            self.engine_manager.send_command("bluie-debug attacks black")
        elif mode.startswith("ATTACKSTO_"):
            sq_idx = self.highlight_manager.selected_square
            if sq_idx is not None:
                files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
                col = sq_idx % 8
                row = 8 - (sq_idx // 8)
                sq_str = f"{files[col]}{row}"
                
                side = "white" if "WHITE" in mode else "black"
                self.engine_manager.send_command(f"bluie-debug attacksto {sq_str} {side}")
            else:
                self.highlight_manager.debug_overlay_squares = []
                self.signals.state_changed.emit()

    def handle_debug_overlay_received(self, otype: str, hex_bb: str) -> None:
        """Parses the received engine threat bitboard and triggers a board repaint."""
        try:
            val = int(hex_bb, 16)
            squares = []
            for i in range(64):
                if (val >> i) & 1:
                    squares.append(i)
                    
            self.highlight_manager.debug_overlay_squares = squares
            self.signals.state_changed.emit()
        except ValueError:
            logger.error(f"Failed to parse debug overlay bitboard hex: {hex_bb}")

    def cleanup(self) -> None:
        """
        Terminates the engine subprocess cleanly. Called on window close.
        """
        logger.info("Cleaning up GameController: terminating C++ engine...")
        self.engine_manager.quit_engine()
