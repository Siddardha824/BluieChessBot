# gui/controllers/handlers/overlay_handler.py

from PySide6.QtCore import QObject, Signal
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class OverlayHandler(QObject):
    # Signals emitted to request a visual board repaint
    request_repaint = Signal()

    def __init__(self, engine_manager, board_state, highlight_manager, parent: QObject | None = None):
        super().__init__(parent)
        self.engine_manager = engine_manager
        self.board_state = board_state
        self.highlight_manager = highlight_manager

        # Connect engine signal
        self.engine_manager.debug_overlay_received.connect(self.handle_debug_overlay_received)

    def set_debug_overlay_mode(self, mode: str) -> None:
        """Sets the active debug overlay mode and triggers query."""
        self.highlight_manager.debug_overlay_mode = mode
        self.query_active_debug_overlay()

    def query_active_debug_overlay(self) -> None:
        """Sends the appropriate uci debug command to request threat overlays."""
        mode = self.highlight_manager.debug_overlay_mode
        if mode == "NONE":
            self.highlight_manager.debug_overlay_squares = []
            self.request_repaint.emit()
            return
            
        fen = self.board_state.get_fen()
        self.engine_manager.send_position(fen)
        
        if mode == "WHITE_ATTACKS":
            self.engine_manager.send_command("bluie-debug attacks white")
        elif mode == "BLACK_ATTACKS":
            self.engine_manager.send_command("bluie-debug attacks black")
        elif mode == "ENGINE_LEGALS":
            self.engine_manager.send_command("bluie-debug legalmoves")
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
                self.request_repaint.emit()

    def handle_debug_overlay_received(self, otype: str, value: str) -> None:
        """Parses the received engine threat bitboard or legal moves list and triggers a board repaint."""
        try:
            if otype == "ENGINE_LEGALS":
                # Stash it directly in BoardState
                self.board_state.cached_engine_legal_moves = value.split()
                
                # If active debug overlay mode is ENGINE_LEGALS, highlight all destination squares
                if self.highlight_manager.debug_overlay_mode == "ENGINE_LEGALS":
                    squares = []
                    for move_str in self.board_state.cached_engine_legal_moves:
                        if len(move_str) >= 4:
                            to_coord = move_str[2:4]
                            to_idx = self.board_state.coordinate_to_index(to_coord)
                            if to_idx is not None and to_idx not in squares:
                                squares.append(to_idx)
                    self.highlight_manager.debug_overlay_squares = squares
                    self.request_repaint.emit()
            else:
                val = int(value, 16)
                squares = []
                for i in range(64):
                    if (val >> i) & 1:
                        squares.append(i)
                        
                self.highlight_manager.debug_overlay_squares = squares
                self.request_repaint.emit()
        except Exception as e:
            logger.error(f"Failed to parse debug overlay value '{value}' for type '{otype}': {e}", exc_info=True)
