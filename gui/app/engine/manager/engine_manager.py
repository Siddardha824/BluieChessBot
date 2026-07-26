"""Engine manager facade module.

This module provides the EngineManager class, which acts as a unified entry
point and facade for all active chess engine sessions and models in the system.
"""

from PySide6.QtCore import QObject, Signal, QProcess

from ..services.engine_service import EngineService
from ..models.engines import Engines
from gui.utils import get_logger

logger = get_logger(__name__)


class EngineManager(QObject):
    """Provide a facade and unified entry point for all chess engine operations.

    This class manages active engine subprocess sessions and their corresponding data
    models, multiplexing signals across the application.

    Signals:
        engine_added: Emitted when a new engine is successfully added (engine_name, engine_status).
        engine_removed: Emitted when an engine is removed from the registry (engine_name).

        engine_info_updated: Emitted when engine metadata is updated (engine_name, info_model).
        engine_settings_updated: Emitted when engine configuration settings are updated.
        engine_analysis_updated: Emitted when engine search telemetry updates.
        engine_ready: Emitted when the engine process signals it is ready.
        engine_stopped: Emitted when the engine process terminates.
        engine_error: Emitted when a process error occurs.
        best_move_updated: Emitted when a search finds a new best move.
    """

    # Multiplexed Model Structure Signals
    engine_added = Signal(str, object)
    engine_removed = Signal(str)

    # Multiplexed Model Data Update Signals
    engine_info_updated = Signal(str, object)
    engine_settings_updated = Signal(str, object)
    engine_analysis_updated = Signal(str, object)

    # Multiplexed Service Event Signals
    engine_ready = Signal(str)
    engine_stopped = Signal(str, int, QProcess.ExitStatus)
    engine_error = Signal(str, str)
    best_move_updated = Signal(str, str)

    def __init__(self, parent):
        """Initialize the engine manager.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self.engines = Engines(self)
        self._services: dict[str, EngineService] = {}

        self.engines.engine_added.connect(self.engine_added)
        self.engines.engine_removed.connect(self.engine_removed)

        logger.info("Engine manager initialized")

    def create_engine(self, engine_name: str) -> bool:
        """Create a new engine session and register its data model and service signals.

        Wires data model signals (info, settings, analysis) and process-level service signals
        (ready, stopped, error, best_move_updated) to multiplexed signals.

        Args:
            engine_name: The unique identifier for the engine.

        Returns:
            True if the engine was successfully registered, False otherwise.
        """

        if engine_name in self._services:
            logger.warning("Engine '%s' already exists.", engine_name)
            return True

        engine_status = self.engines.add_engine(engine_name)
        if not engine_status:
            return False

        # Wire Data Model Signals
        engine_status.info.info_updated.connect(
            lambda name=engine_name, info_data=engine_status.info:
                self.engine_info_updated.emit(name, info_data)
        )

        engine_status.settings.settings_updated.connect(
            lambda name=engine_name, settings_data=engine_status.settings:
                self.engine_settings_updated.emit(name, settings_data)
        )

        engine_status.analysis.analysis_state_changed.connect(
            lambda name=engine_name, analysis_data=engine_status.analysis:
                self.engine_analysis_updated.emit(name, analysis_data)
        )

        service = EngineService(engine_status, self)

        # Wire Service Event Signals
        service.engine_ready.connect(
            lambda name=engine_name: self.engine_ready.emit(name)
        )
        service.engine_stopped.connect(
            lambda code, status, name=engine_name: self.engine_stopped.emit(name, code, status)
        )
        service.engine_error.connect(
            lambda msg, name=engine_name: self.engine_error.emit(name, msg)
        )
        service.best_move_updated.connect(
            lambda move, name=engine_name: self.best_move_updated.emit(name, move)
        )

        self._services[engine_name] = service
        logger.info("Engine created: %s", engine_name)
        return True

    def remove_engine(self, engine_name: str):
        """Remove a registered engine and stop its subprocess.

        Args:
            engine_name: The identifier of the engine to remove.
        """
        service = self._services.pop(engine_name, None)
        if service:
            service.stop()
            self.engines.remove_engine(engine_name)
            service.deleteLater()
            logger.info("Engine removed: %s", engine_name)
        else:
            logger.warning("Cannot remove missing engine: %s", engine_name)

    def shutdown(self):
        """Shut down all active engine subprocesses and clear the registries."""
        logger.info("Shutting down all engines")
        for service in list(self._services.values()):
            service.stop()
        self._services.clear()
        self.engines.clear()

    def _get_service(self, engine_name: str) -> EngineService | None:
        """Retrieve the service wrapper for a specific engine.

        Args:
            engine_name: The identifier of the engine.

        Returns:
            The EngineService wrapper if found, None otherwise.
        """
        service = self._services.get(engine_name)
        if not service:
            logger.warning("Command failed: Engine '%s' not found.", engine_name)
        return service

    # --- Public Command API ---
    def setup_engine(self, engine_name: str, engine_path: str):
        """Create and start a chess engine subprocess.

        Args:
            engine_name: The identifier for the engine.
            engine_path: The executable path of the engine.
        """
        success = self.create_engine(engine_name)
        if not success:
            logger.error(f"Failed to create engine {engine_name}")

        success = self.start(engine_name, engine_path)
        if not success:
            logger.error(f"Failed to start engine {engine_name} at {engine_path}")

    def start(self, engine_name: str, fallback_path: str = "") -> bool:
        """Start the engine subprocess.

        Args:
            engine_name: The identifier of the engine.
            fallback_path: Optional path to use if no path is configured.

        Returns:
            True if started successfully, False otherwise.
        """
        if service := self._get_service(engine_name):
            return service.start(fallback_path)
        return False

    def stop(self, engine_name: str):
        """Stop the engine subprocess.

        Args:
            engine_name: The identifier of the engine.
        """
        if service := self._get_service(engine_name):
            service.stop()

    def send(self, engine_name: str, command: str):
        """Send a raw UCI command string to the engine subprocess stdin.

        Args:
            engine_name: The identifier of the engine.
            command: The raw UCI command string.
        """
        if service := self._get_service(engine_name):
            service.send(command)

    def update_settings(self, engine_name: str, **kwargs):
        """Update configurations for a specific engine.

        Args:
            engine_name: The identifier of the engine.
            **kwargs: Keyword settings arguments (e.g. threads=4).
        """
        if service := self._get_service(engine_name):
            service.update_settings(**kwargs)

    def is_running(self, engine_name: str) -> bool:
        """Check if the engine process is currently running.

        Args:
            engine_name: The identifier of the engine.

        Returns:
            True if running, False otherwise.
        """
        if service := self._get_service(engine_name):
            return service.is_running()
        return False

    def is_ready(self, engine_name: str):
        """Send an isready query to the engine.

        Args:
            engine_name: The identifier of the engine.
        """
        if service := self._get_service(engine_name):
            service.is_ready()

    def set_position_startpos(self, engine_name: str):
        """Set the board position to the standard starting position.

        Args:
            engine_name: The identifier of the engine.
        """
        if service := self._get_service(engine_name):
            service.set_position_startpos()

    def set_position_fen(self, engine_name: str, fen: str):
        """Set the board position from a FEN string.

        Args:
            engine_name: The identifier of the engine.
            fen: FEN string representing the position.
        """
        if service := self._get_service(engine_name):
            service.set_position_fen(fen)

    def set_options(self, engine_name: str, hash: int = -1, threads: int = -1):
        """Configure engine options (hash size and thread counts).

        Args:
            engine_name: The identifier of the engine.
            hash: Transposition table size in MB.
            threads: Number of search threads.
        """
        if service := self._get_service(engine_name):
            if hash > 0:
                service.update_settings(hash_size=hash)
            if threads > 0:
                service.update_settings(threads=threads)
            service.set_options()

    def go(self, engine_name: str):
        """Execute a search using the constraints stored in the engine's settings.

        Args:
            engine_name: The identifier of the engine.
        """
        if service := self._get_service(engine_name):
            service.go()

    def go_depth(self, engine_name: str, depth: int):
        """Start search up to a maximum ply depth.

        Args:
            engine_name: The identifier of the engine.
            depth: Maximum search depth in plies.
        """
        if service := self._get_service(engine_name):
            service.go_depth(depth)

    def go_infinite(self, engine_name: str):
        """Start search in infinite mode.

        Args:
            engine_name: The identifier of the engine.
        """
        if service := self._get_service(engine_name):
            service.go_infinite()

    def go_time(self, engine_name: str, ms: int):
        """Start search for a maximum time duration.

        Args:
            engine_name: The identifier of the engine.
            ms: Maximum search time in milliseconds.
        """
        if service := self._get_service(engine_name):
            service.go_time(ms)

    def go_nodes(self, engine_name: str, nodes: int):
        """Start search for a maximum node count.

        Args:
            engine_name: The identifier of the engine.
            nodes: Maximum nodes to evaluate.
        """
        if service := self._get_service(engine_name):
            service.go_nodes(nodes)

    def stop_search(self, engine_name: str):
        """Stop the active search.

        Args:
            engine_name: The identifier of the engine.
        """
        if service := self._get_service(engine_name):
            service.stop_search()

    def asdict(self, engine_name: str) -> dict | None:
        """Convert the engine status model to a dictionary.

        Args:
            engine_name: The identifier of the engine.

        Returns:
            The serialized engine status dictionary, or None if not found.
        """
        if service := self._get_service(engine_name):
            return service.status.asdict()
        return None

    def load_settings(self, engines_dict: dict):
        """Load engine configurations from a serialized dictionary.

        Args:
            engines_dict: Dict mapping engine names to settings payload.
        """
        for engine_name, engine_data in engines_dict.items():
            self.create_engine(engine_name)

            if "settings" in engine_data:
                self.update_settings(engine_name, **engine_data["settings"])

    def get_export_state(self) -> dict:
        """Export the active states and settings of all registered engines.

        Returns:
            A dictionary containing active engine profiles.
        """
        state = {}
        for name in self.engines.active_engines:
            engine_dict = self.asdict(name)
            if engine_dict:
                state[name] = engine_dict
        return state
