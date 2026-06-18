from PySide6.QtCore import QObject, Signal, QTimer
import chess
from ..models.game_state import GameState, GameModes
from gui.app.board.services.board_mapper import BoardMapper
from gui.utils import get_logger

logger = get_logger(__name__)

class GameManager(QObject):
    game_over = Signal(str, str)  # Emits (result, reason)

    def __init__(self, app_manager, parent=None):
        super().__init__(parent)
        self._manager = app_manager
        self._state = GameState(self)
        
        # Internal configuration for engine constraint settings per session
        self.engine_settings = {
            "main": {
                "constraint_mode": "Depth",
                "max_depth": 3,
                "max_time_ms": 1000,
                "max_nodes": 10000,
                "engine_path": ""
            },
            "white_engine": {
                "constraint_mode": "Depth",
                "max_depth": 3,
                "max_time_ms": 1000,
                "max_nodes": 10000,
                "engine_path": ""
            },
            "black_engine": {
                "constraint_mode": "Depth",
                "max_depth": 4,
                "max_time_ms": 1000,
                "max_nodes": 10000,
                "engine_path": ""
            }
        }
        self.auto_analyze = True
        self.is_paused = False
        
        # Player vs Engine settings
        self.human_color = chess.WHITE  # Default human is White
        
        # Engine vs Engine settings
        self.move_delay_ms = 500
        self._loop_timer = QTimer(self)
        self._loop_timer.setSingleShot(True)
        self._loop_timer.timeout.connect(self._on_loop_timeout)
        
        # Wire signals
        self._connected_sessions = set()
        self._connect_signals()

    @property
    def constraint_mode(self) -> str:
        return self.engine_settings["main"]["constraint_mode"]

    @constraint_mode.setter
    def constraint_mode(self, val: str):
        self.engine_settings["main"]["constraint_mode"] = val

    @property
    def max_depth(self) -> int:
        return self.engine_settings["main"]["max_depth"]

    @max_depth.setter
    def max_depth(self, val: int):
        self.engine_settings["main"]["max_depth"] = val

    @property
    def max_time_ms(self) -> int:
        return self.engine_settings["main"]["max_time_ms"]

    @max_time_ms.setter
    def max_time_ms(self, val: int):
        self.engine_settings["main"]["max_time_ms"] = val

    @property
    def max_nodes(self) -> int:
        return self.engine_settings["main"]["max_nodes"]

    @max_nodes.setter
    def max_nodes(self, val: int):
        self.engine_settings["main"]["max_nodes"] = val

    @property
    def state(self) -> GameState:
        return self._state

    def _connect_signals(self):
        # Listen for board position changes
        self._manager.board.position_changed.connect(self._on_position_changed)
        # Listen for engine best moves
        self._manager.main_session.best_move_updated.connect(self._on_best_move_updated)
        self._connected_sessions.add("main")

    def start_game(self):
        logger.info("Starting new game in mode: %s", self.state.mode.name)
        
        # Determine and start required engine sessions manually
        mode = self.state.mode
        if mode == GameModes.ENGINE_VS_ENGINE:
            self._start_session_if_needed("white_engine")
            self._start_session_if_needed("black_engine")
        else:
            self._start_session_if_needed("main")

        self._manager.board.new_game()
        self.is_paused = False
        self._trigger_next_action()

    def _start_session_if_needed(self, session_id: str):
        session = self._manager.engine.get_session(session_id)
        if session is None:
            session = self._manager.engine.create_session(session_id)
        
        if session is not None:
            if session_id not in self._connected_sessions:
                session.best_move_updated.connect(self._on_best_move_updated)
                self._connected_sessions.add(session_id)
                logger.info("Connected best_move_updated for engine session: %s", session_id)
        
        if session is not None and not session.is_running():
            logger.info("Starting engine session manually: %s", session_id)
            path = self.engine_settings.get(session_id, {}).get("engine_path")
            self._manager.start_engine(engine_path=path if path else None, session_id=session_id)

    def stop_game(self):
        logger.info("Stopping game/search")
        self.is_paused = True
        self._loop_timer.stop()
        
        # Stop search on all running engine sessions
        for session in list(self._manager.engine.sessions.values()):
            if session.is_running():
                session.stop_search()

    def set_mode(self, mode: GameModes):
        self.stop_game()
        self.state.mode = mode
        self.is_paused = False

    def _on_position_changed(self, fen: str):
        if self.is_paused:
            return
        self._trigger_next_action()

    def _trigger_next_action(self):
        board_state = self._manager.board.getSession.getBoard
        
        # Check game over conditions
        if board_state.is_game_over():
            result = board_state.result()
            reason = "Game Over"
            if board_state.is_checkmate():
                reason = "Checkmate"
            elif board_state.is_stalemate():
                reason = "Stalemate"
            elif board_state.is_insufficient_material():
                reason = "Insufficient Material"
            elif board_state.is_fivefold_repetition() or board_state.is_threefold_repetition():
                reason = "Repetition"
            elif board_state.is_seventyfive_moves() or board_state.is_fifty_moves():
                reason = "50-move Rule"
                
            self.state.result = result
            self.state.result_reason = reason
            self.stop_game()
            self.game_over.emit(result, reason)
            return

        mode = self.state.mode

        if mode == GameModes.ANALYSIS:
            if self.auto_analyze:
                self._start_engine_search()
                
        elif mode in (GameModes.PLAY_WHITE, GameModes.PLAY_BLACK):
            # PLAY_WHITE means Human is White (Engine is Black)
            # PLAY_BLACK means Human is Black (Engine is White)
            engine_color = chess.BLACK if mode == GameModes.PLAY_WHITE else chess.WHITE
            if board_state.turn == engine_color:
                self._start_engine_search()
                
        elif mode == GameModes.ENGINE_VS_ENGINE:
            # Trigger search after move delay
            self._loop_timer.start(self.move_delay_ms)

    def _on_loop_timeout(self):
        if self.is_paused:
            return
        self._start_engine_search()

    def _start_engine_search(self):
        mode = self.state.mode
        if mode == GameModes.ENGINE_VS_ENGINE:
            board_state = self._manager.board.getSession.getBoard
            session_id = "white_engine" if board_state.turn == chess.WHITE else "black_engine"
            session = self._manager.engine.get_session(session_id)
        else:
            session_id = "main"
            session = self._manager.main_session
            
        if session is None or not session.is_running():
            logger.error("Attempted engine search but session is not running or is None")
            return
            
        session.stop_search()
        
        # Synchronize board position FEN to engine immediately before starting search
        fen = self._manager.board.getSession.fen
        session.set_position_fen(fen)
        
        # Apply search constraints based on session-specific settings
        settings = self.engine_settings.get(session_id, self.engine_settings["main"])
        constraint_mode = settings["constraint_mode"]
        
        if constraint_mode == "Depth":
            session.go_depth(settings["max_depth"])
        elif constraint_mode == "Time":
            session.go_time(settings["max_time_ms"])
        elif constraint_mode == "Nodes":
            session.go_nodes(settings["max_nodes"])
        else:
            session.go_infinite()

    def _on_best_move_updated(self, best_move: str):
        if self.is_paused:
            return
            
        board_state = self._manager.board.getSession.getBoard
        mode = self.state.mode
        
        # In Analysis mode, we just show the best move, we do not play it!
        if mode == GameModes.ANALYSIS:
            return
            
        # In Play modes or Engine vs Engine, we execute the move on the board
        if mode == GameModes.ENGINE_VS_ENGINE:
            expected_session_id = "white_engine" if board_state.turn == chess.WHITE else "black_engine"
            expected_session = self._manager.engine.get_session(expected_session_id)
            if self.sender() != expected_session:
                logger.warning("Received best move from inactive engine session in engine vs engine mode")
                return
            is_engine_turn = True
        else:
            engine_color = chess.BLACK if mode == GameModes.PLAY_WHITE else chess.WHITE
            is_engine_turn = (board_state.turn == engine_color)
            if is_engine_turn:
                if self.sender() != self._manager.main_session:
                    logger.warning("Received best move from non-main engine session in play mode")
                    return
        
        if is_engine_turn:
            success = self._manager.board.make_move(best_move)
            if not success:
                logger.error("Engine played illegal move: %s", best_move)
