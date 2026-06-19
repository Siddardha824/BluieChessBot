from PySide6.QtCore import QObject, Signal

from ..models.board_state import BoardState
from ..services.move_executor import MoveExecutor
from gui.utils import get_logger


logger = get_logger(__name__)

class BoardManager(QObject):
    position_changed = Signal(str)    

    def __init__(self, parent=None):
        super().__init__(parent)

        logger.info("Initializing board manager")
        self._board_state = BoardState(self)
        self._board_state.position_changed.connect(
            self.position_changed.emit
        )

    @property
    def session(self) -> BoardState:
        return self._board_state

    def make_move(self, move: str) -> bool:
        success = MoveExecutor.make_move(self._board_state, move)
        if success:
            logger.info("Move applied: %s", move)
        else:
            logger.warning("Move rejected: %s", move)
        return success
    
    def undo_move(self) -> str | None:
        return MoveExecutor.undo_move(self._board_state)

    def new_game(self):
        logger.info("Starting new game")
        self._board_state.reset()

    def load_fen(self, fen: str):
        logger.info("Loading FEN: %s", fen)
        self._board_state.set_fen(fen)

    def get_san_for_move(self, uci_move: str) -> str:
        """
        Converts a single UCI move (e.g. 'e2e4') valid in the current position
        into its SAN representation (e.g. 'e4').
        """
        import chess
        try:
            move = chess.Move.from_uci(uci_move)
            board = self._board_state.board
            if move in board.legal_moves:
                return board.san(move)
        except Exception as e:
            logger.debug("Failed to get SAN for move %s: %s", uci_move, e)
        return uci_move

    def format_uci_sequence(self, uci_moves: list[str]) -> str:
        """
        Converts a list/sequence of UCI moves starting from the current board position
        into a formatted SAN string (e.g. '1. e4 e5 2. Nf3 Nc6').
        """
        if not uci_moves:
            return ""
            
        import chess
        board = self._board_state.view_board.copy()
        san_moves = []
        
        for move_str in uci_moves:
            try:
                move = chess.Move.from_uci(move_str)
                if move in board.legal_moves:
                    san = board.san(move)
                    if board.turn == chess.WHITE:
                        san_moves.append(f"{board.fullmove_number}. {san}")
                    else:
                        if not san_moves:
                            san_moves.append(f"{board.fullmove_number}... {san}")
                        else:
                            san_moves.append(san)
                    board.push(move)
                else:
                    san_moves.append(move_str)
            except Exception as e:
                logger.debug("Failed to parse/format UCI move %s: %s", move_str, e)
                san_moves.append(move_str)
                
        return " ".join(san_moves)

