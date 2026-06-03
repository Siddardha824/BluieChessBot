from PySide6.QtCore import QObject, Signal
import chess

class BoardState(QObject):
    position_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._board = chess.Board()

    @property
    def board(self) -> chess.Board:
        return self._board

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
            return

        self._board.set_fen(fen)
        self.position_changed.emit(self._board.fen())

    def reset(self):
        self._board.reset()
        self.position_changed.emit(self._board.fen())

    def push(self, move: chess.Move):
        self._board.push(move)
        self.position_changed.emit(self._board.fen())

    def can_undo(self) -> bool:
        return bool(self._board.move_stack)

    def pop(self) -> chess.Move:
        if not self._board.move_stack:
            raise IndexError("No moves to undo")

        move = self._board.pop()
        self.position_changed.emit(self._board.fen())
        return move