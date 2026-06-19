from PySide6.QtCore import QObject, Signal
import chess
from gui.utils import get_logger


logger = get_logger(__name__)

class BoardState(QObject):
    position_changed = Signal(str)
    view_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._board = chess.Board()
        # Cache list of chess.Board positions representing the stack of boards
        # _positions[0] is the starting board.
        # _positions[i] is the board after move i.
        self._positions = [self._board.copy()]
        self._view_index = 0

    @property
    def board(self) -> chess.Board:
        return self._board

    @property
    def view_board(self) -> chess.Board:
        return self._positions[self._view_index]

    @property
    def starting_fen(self) -> str:
        return self._positions[0].fen()

    @property
    def view_index(self) -> int:
        return self._view_index

    @view_index.setter
    def view_index(self, index: int):
        max_idx = len(self._board.move_stack)
        index = max(0, min(max_idx, index))
        if self._view_index != index:
            logger.debug("View index changed to %s / %s", index, max_idx)
            self._view_index = index
            self._sync_view(position_changed=False)

    @property
    def fen(self) -> str:
        return self._board.fen()

    @property
    def turn(self) -> chess.Color:
        return self._board.turn

    @property
    def fullmove_number(self) -> int:
        return self._board.fullmove_number

    @property
    def halfmove_clock(self) -> int:
        return self._board.halfmove_clock
    
    @property
    def move_stack(self) -> list[chess.Move]:
        return self._board.move_stack.copy()

    def set_fen(self, fen: str):
        if fen == self._board.fen():
            logger.debug("FEN unchanged; skipping update")
            return

        self._board.set_fen(fen)
        self._positions = [self._board.copy()]
        self._view_index = 0
        logger.debug("Board FEN updated: %s", self._board.fen())
        self._sync_view(position_changed=True)

    def reset(self):
        self._board.reset()
        self._positions = [self._board.copy()]
        self._view_index = 0
        logger.debug("Board reset to starting position")
        self._sync_view(position_changed=True)

    def push(self, move: chess.Move):
        # Truncate moves in _board if we were viewing a past position
        if self._view_index < len(self._board.move_stack):
            logger.info("Truncating board history from index %s", self._view_index)
            while len(self._board.move_stack) > self._view_index:
                self._board.pop()
            self._positions = self._positions[:self._view_index + 1]
                
        self._board.push(move)
        
        # Cache the new position by copying the previous one and pushing the move
        new_board = self._positions[-1].copy()
        new_board.push(move)
        self._positions.append(new_board)
        
        self._view_index = len(self._board.move_stack)
        logger.debug("Board move pushed: %s", move.uci())
        self._sync_view(position_changed=True)

    def can_undo(self) -> bool:
        return bool(self._board.move_stack)

    def pop(self) -> chess.Move:
        if not self._board.move_stack:
            logger.warning("Undo requested with no moves in stack")
            raise IndexError("No moves to undo")

        move = self._board.pop()
        self._positions.pop()
        
        if self._view_index > len(self._board.move_stack):
            self._view_index = len(self._board.move_stack)
            
        logger.debug("Board move popped: %s", move.uci())
        self._sync_view(position_changed=True)
        return move

    def _sync_view(self, position_changed: bool = True):
        if position_changed:
            self.position_changed.emit(self._board.fen())
        self.view_changed.emit()
