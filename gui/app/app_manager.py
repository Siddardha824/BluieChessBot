from PySide6.QtCore import QObject, Signal
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PySide6.QtCore import QProcess

from .board import BoardManager
from .theme import ThemeManager
from .settings import SettingsManager
from .game import GameManager
from .engine import EngineManager
from gui.utils import get_logger

logger = get_logger(__name__)

class AppManager(QObject):
    """
    Root application object.

    Owns and wires together all major subsystems.
    """
    # Passing the module signals

    # Theme Module
    theme_changed = Signal()

    # Game Module
    game_started = Signal()
    game_stopped = Signal()
    game_saved = Signal()
    game_over = Signal(str, str)

    # Board Module
    board_state_changed = Signal(object)

    # Engine Module
    engine_added = Signal(str, object)
    engine_removed = Signal(str)
    engine_info_updated = Signal(str, object)
    engine_settings_updated = Signal(str, object)
    engine_analysis_updated = Signal(str, object)
    engine_ready = Signal(str)
    engine_stopped = Signal(str, int, QProcess.ExitStatus)
    engine_error = Signal(str, str)

    def __init__(self, parent):
        super().__init__(parent)

        logger.info("Initializing app manager")

        self._board = BoardManager(self)
        self._engines = EngineManager(self)
        self._theme = ThemeManager(self)
        self._settings = SettingsManager(self)
        self._game = GameManager(self)

        self._connect_modules()

        self.startup()

        logger.info("App manager initialized")

    @property
    def board(self) -> BoardManager:
        return self._board
    
    @property
    def engines(self) -> EngineManager:
        return self._engines
    
    @property
    def theme(self) -> ThemeManager:
        return self._theme
    
    @property
    def settings(self) -> SettingsManager:
        return self._settings
    
    @property
    def game(self) -> GameManager:
        return self._game
    
    def startup(self):
        self.settings.load()
    
    def shut_down(self):
        self.save()
        self.game.stop_game()
        self.engines.shutdown()

    def _connect_modules(self):

        # Connecting Board Manager, Engine Manager to Game Manager
        self.board.view_changed.connect(self.game.on_view_changed)
        self.engines.best_move_updated.connect(self.game.on_best_move_updated)

        self.game.setup_engine.connect(self.engines.setup_engine)
        self.game.remove_engine.connect(self.engines.remove_engine)
        self.game.set_engine_position.connect(self.engines.set_position_fen)
        self.game.start_engine_search.connect(self.engines.go)
        self.game.stop_engine_search.connect(self.engines.stop_search)
        self.game.new_game.connect(self.board.new_game)
        self.game.make_move.connect(self.board.make_move)

        # Connecting Settings module
        self.settings.loaded.connect(self.load_settings)

        self._connect_ui_pass_on_signals()

    def _connect_ui_pass_on_signals(self):
        self.theme.theme_changed.connect(self.theme_changed.emit)

        self.board.view_changed.connect(self.board_state_changed.emit)

        self.game.game_started.connect(self.game_started.emit)
        self.game.game_over.connect(self.game_over.emit)
        self.game.game_saved.connect(self.game_saved.emit)
        self.game.game_stopped.connect(self.game_stopped.emit)

        self.engines.engine_added.connect(self.engine_added.emit)
        self.engines.engine_removed.connect(self.engine_removed.emit)
        self.engines.engine_info_updated.connect(self.engine_info_updated.emit)
        self.engines.engine_settings_updated.connect(self.engine_settings_updated.emit)
        self.engines.engine_analysis_updated.connect(self.engine_analysis_updated.emit)
        self.engines.engine_ready.connect(self.engine_ready.emit)
        self.engines.engine_stopped.connect(self.engine_stopped.emit)
        self.engines.engine_error.connect(self.engine_error.emit)

    def load_settings(self, settings: dict):
        if "theme" in settings:
            self.theme.load_theme_from_settings(settings["theme"])

        if "engines" in settings:
            self.engines.load_settings(settings["engines"])

    def export_pgn(self, filepath: str):
        active_engines = self.game.get_active_engines()
        root_node = self.board.get_export_state()
        engine_info = {}

        if active_engines:
            for engine in active_engines:
                engine_info[engine] = self.engines.asdict(engine)

        self.game.save_game(filepath, root_node, engine_info)        

    def save(self):

        theme_settings = self.theme.get_export_state()
        engines_settings = self.engines.get_export_state()

        self.settings.save(
            theme=theme_settings,
            engines=engines_settings
        )
