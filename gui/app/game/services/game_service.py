from PySide6.QtCore import QObject
import chess
from ..models.game_state import GameState, GameMode, MatchStatus

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.app.app_manager import AppManager
    from gui.app.board.services.move_node import MoveNode, ChildMoveNode

from gui.utils import get_logger
logger = get_logger(__name__)

class GameService(QObject):
    def __init__(self, parent, state: GameState, app_manager: AppManager):
        super().__init__(parent)

        self._state = state
        self._app = app_manager

        self._white_engine: str | None = None
        self._black_engine: str | None = None

        self._app.board.view_changed.connect(self._on_view_changed)
        self._app.engines.best_move_updated.connect(self._on_best_move_updated)

        logger.info("Game Service Initialized")

    def _setup_engine(self, engine_name: str, engine_path: str):
        if not engine_path:
            logger.error(f"Cannot setup an engine {engine_name}: No path provided")
            return False
        
        success = self._app.engines.create_engine(engine_name)
        if not success:
            logger.error(f"Error creating an engine with name: {engine_name}")
            return False
        
        success = self._app.engines.start(engine_name, engine_path)
        if not success:
            logger.error(f"Error starting the engine {engine_name} at {engine_path}")
            return False
        
        return True
    
    def _cleanup_engines(self):
        if self._white_engine:
            self._app.engines.remove_engine(self._white_engine)
        if self._black_engine:
            self._app.engines.remove_engine(self._black_engine)

        self._white_engine = None
        self._black_engine = None

    def start_game(self, white_path: str = "", black_path: str = ""):
        logger.info(f"Game Service starting a game in Mode: {self._state.mode}")

        self._cleanup_engines()

        match self._state.mode:
            case GameMode.ANALYSIS:
                self._start_analysis(white_path)
            case GameMode.PLAY_WHITE:
                self._start_game_white(black_path)
            case GameMode.PLAY_BLACK:
                self._start_game_black(white_path)
            case GameMode.ENGINE_VS_ENGINE:
                self._start_game_engine(white_path, black_path)

        self._app.board.new_game()
        self._state.reset()

        self._trigger_next_action()

    def end_game(self):
        if self._white_engine:
            self._app.engines.stop_search(self._white_engine)
        if self._black_engine:
            self._app.engines.stop_search(self._black_engine)

    def abort_game(self):
        if self._white_engine:
            self._app.engines.stop_search(self._white_engine)
        if self._black_engine:
            self._app.engines.stop_search(self._black_engine)
            
        self._state.match_status = MatchStatus.ABORTED

    def _start_analysis(self, engine_path: str):
        self._white_engine = "Analysis"
        self._setup_engine(self._white_engine, engine_path)

    def _start_game_white(self, black_engine_path: str):
        self._black_engine = "Opponent"
        self._setup_engine(self._black_engine, black_engine_path)

    def _start_game_black(self, white_engine_path: str):
        self._white_engine = "Opponent"
        self._setup_engine(self._white_engine, white_engine_path)

    def _start_game_engine(self, white_engine_path: str, black_engine_path: str):
        self._white_engine = "White"
        self._black_engine = "Black"
        self._setup_engine(self._white_engine, white_engine_path)
        self._setup_engine(self._black_engine, black_engine_path)

    def _on_view_changed(self, node: MoveNode | ChildMoveNode):
        board = node.board()
        self._state.current_turn = board.turn

        if board.is_checkmate():
            self._state.match_status = MatchStatus.CHECKMATE
            self.end_game()

        if board.is_game_over(claim_draw=True):
            self._state.match_status = MatchStatus.DRAW
            self.end_game()
            return

        if self._state.match_status == MatchStatus.ACTIVE:
            self._trigger_next_action()
        

    def _on_best_move_updated(self, engine_name: str, best_move: str):
        expected_engine = self._get_active_engine_for_turn()

        if expected_engine and engine_name == expected_engine:
            if self._state.mode in [GameMode.PLAY_WHITE, GameMode.PLAY_BLACK, GameMode.ENGINE_VS_ENGINE]:
                logger.info("%s played: %s", engine_name, best_move)
                self._app.board.make_move(best_move)

    def _trigger_next_action(self):
        if self._state.match_status != MatchStatus.ACTIVE:
            return
        
        active_engine = self._get_active_engine_for_turn()

        if self._state.mode == GameMode.ANALYSIS and self._white_engine:
            self._start_engine_search(self._white_engine)
        elif active_engine:
            self._start_engine_search(active_engine)

    def _get_active_engine_for_turn(self) -> str | None:
        if self._state.current_turn == chess.WHITE:
            return self._white_engine
        else:
            return self._black_engine
        
    def _start_engine_search(self, engine_name: str):
        current_fen = self._app.board.get_fen()
        logger.info("Triggering %s search for FEN: %s", engine_name, current_fen)
        
        self._app.engines.set_position_fen(engine_name, current_fen)
        self._app.engines.go(engine_name)
