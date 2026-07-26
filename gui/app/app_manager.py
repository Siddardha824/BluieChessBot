"""Application manager entry point module.

This module provides the AppManager class, which acts as the root coordinator
and facade for the entire chess application, wiring together the game state,
board display, chess engine process control, themes, and settings.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QProcess

from .board import BoardManager
from .theme import ThemeManager
from .settings import SettingsManager
from .game import GameManager
from .engine import EngineManager
from gui.utils import get_logger

logger = get_logger(__name__)


class AppManager(QObject):
    """Root application controller and coordinator.

    This manager owns and wires together all major subsystems including the Board,
    Engine, Game, Settings, and Theme modules. It acts as the central hub for
    multiplexing signal notifications from subsystems to the UI layer.

    Signals:
        theme_changed: Emitted when the UI theme changes.
        game_started: Emitted when a new chess game starts.
        game_stopped: Emitted when a chess game is aborted or ended.
        game_saved: Emitted when the current game is saved to disk.
        game_over: Emitted with (result, termination_reason) when a game ends.
        board_state_changed: Emitted when the board view changes with the new active MoveNode.
        engine_added: Emitted when a chess engine is registered (name, status_model).
        engine_removed: Emitted when a chess engine is removed (name).
        engine_info_updated: Emitted when an engine's metadata changes.
        engine_settings_updated: Emitted when an engine's configuration changes.
        engine_analysis_updated: Emitted when engine search telemetry updates.
        engine_ready: Emitted when an engine process is ready.
        engine_stopped: Emitted when an engine process terminates.
        engine_error: Emitted when an engine process encounters an error.
    """

    # Theme Module Signals
    theme_changed = Signal()

    # Game Module Signals
    game_started = Signal()
    game_stopped = Signal()
    game_saved = Signal()
    game_over = Signal(str, str)

    # Board Module Signals
    board_state_changed = Signal(object)

    # Engine Module Signals
    engine_added = Signal(str, object)
    engine_removed = Signal(str)
    engine_info_updated = Signal(str, object)
    engine_settings_updated = Signal(str, object)
    engine_analysis_updated = Signal(str, object)
    engine_ready = Signal(str)
    engine_stopped = Signal(str, int, QProcess.ExitStatus)
    engine_error = Signal(str, str)

    def __init__(self, parent):
        """Initialize the application manager and construct all major subsystems.

        Args:
            parent: The parent QObject for Qt ownership hierarchy.
        """
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
        """Return the BoardManager coordinate and facade controller."""
        return self._board
    
    @property
    def engines(self) -> EngineManager:
        """Return the EngineManager subprocess and session coordinator."""
        return self._engines
    
    @property
    def theme(self) -> ThemeManager:
        """Return the ThemeManager presentation and style manager."""
        return self._theme
    
    @property
    def settings(self) -> SettingsManager:
        """Return the SettingsManager persistence and configuration provider."""
        return self._settings
    
    @property
    def game(self) -> GameManager:
        """Return the GameManager high-level workflow controller."""
        return self._game
    
    def startup(self):
        """Start up the application by loading settings from persistent storage."""
        self.settings.load()
    
    def shut_down(self):
        """Perform a clean shutdown of all systems, saving state and stopping engines."""
        self.save()
        self.game.stop_game()
        self.engines.shutdown()

    def _connect_modules(self):
        """Wire together subsystem interactions and signals internally."""
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
        """Connect internal subsystem signals to multiplexed AppManager public signals."""
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
        """Load and apply configuration settings to theme and engine subsystems.

        Args:
            settings: Dictionary of configuration options.
        """
        if "theme" in settings:
            self.theme.load_theme_from_settings(settings["theme"])

        if "engines" in settings:
            self.engines.load_settings(settings["engines"])

    def export_pgn(self, filepath: str):
        """Export the current game state, move history, and active engine configuration to a PGN file.

        Args:
            filepath: Path to the output PGN file.
        """
        active_engines = self.game.get_active_engines()
        root_node = self.board.get_export_state()
        engine_info = {}

        if active_engines:
            for engine in active_engines:
                engine_info[engine] = self.engines.asdict(engine)

        self.game.save_game(filepath, root_node, engine_info)        

    def save(self):
        """Save the current theme settings and engine profiles to the settings manager."""
        theme_settings = self.theme.get_export_state()
        engines_settings = self.engines.get_export_state()

        self.settings.save(
            theme=theme_settings,
            engines=engines_settings
        )
