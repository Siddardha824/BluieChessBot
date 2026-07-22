from PySide6.QtCore import QObject, Signal, QProcess

from ..services.engine_service import EngineService
from ..models.engines import Engines
from gui.utils import get_logger

logger = get_logger(__name__)

class EngineManager(QObject):
    """
    The Facade and single entry point for all engine operations.
    Exposes unified signals across all active engine sessions and data models.
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
        super().__init__(parent)
        self.engines_model = Engines(self)
        self._services: dict[str, EngineService] = {}
        
        self.engines_model.engine_added.connect(self.engine_added)
        self.engines_model.engine_removed.connect(self.engine_removed)
        
        logger.info("Engine manager initialized")

    def create_engine(self, engine_name: str) -> bool:
        if engine_name in self._services:
            logger.warning("Engine '%s' already exists.", engine_name)
            return True

        status_model = self.engines_model.add_engine(engine_name)
        if not status_model:
            return False

        # Wire Data Model Signals
        status_model.info.info_updated.connect(
            lambda name=engine_name, info_data=status_model.info: 
                self.engine_info_updated.emit(name, info_data)
        )
        
        status_model.analysis.analysis_state_changed.connect(
            lambda name=engine_name, analysis_data=status_model.analysis: 
                self.engine_analysis_updated.emit(name, analysis_data)
        )

        service = EngineService(status_model, self)
        
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
        service = self._services.pop(engine_name, None)
        if service:
            service.stop()
            self.engines_model.remove_engine(engine_name)
            service.deleteLater()
            logger.info("Engine removed: %s", engine_name)
        else:
            logger.warning("Cannot remove missing engine: %s", engine_name)

    def shutdown(self):
        logger.info("Shutting down all engines")
        for service in list(self._services.values()):
            service.stop()
        self._services.clear()
        self.engines_model.clear()

    def _get_service(self, engine_name: str) -> EngineService | None:
        service = self._services.get(engine_name)
        if not service:
            logger.warning("Command failed: Engine '%s' not found.", engine_name)
        return service

    # --- Public Command API ---
    def setup_engine(self, engine_name: str, engine_path: str):
        success = self.create_engine(engine_name)
        if not success:
            logger.error(f"Failed to create engine {engine_name}")

        success = self.start(engine_name, engine_path)
        if not success:
            logger.error(f"Failed to start engine {engine_name} at {engine_path}")

    def start(self, engine_name: str, fallback_path: str = "") -> bool:
        if service := self._get_service(engine_name):
            return service.start(fallback_path)
        return False

    def stop(self, engine_name: str):
        if service := self._get_service(engine_name):
            service.stop()

    def send(self, engine_name: str, command: str):
        if service := self._get_service(engine_name):
            service.send(command)

    def update_settings(self, engine_name: str, **kwargs):
        if service := self._get_service(engine_name):
            service.update_settings(**kwargs)

    def is_running(self, engine_name: str) -> bool:
        if service := self._get_service(engine_name):
            return service.is_running()
        return False

    def is_ready(self, engine_name: str):
        if service := self._get_service(engine_name):
            service.is_ready()

    def set_position_startpos(self, engine_name: str):
        if service := self._get_service(engine_name):
            service.set_position_startpos()

    def set_position_fen(self, engine_name: str, fen: str):
        if service := self._get_service(engine_name):
            service.set_position_fen(fen)

    def set_options(self, engine_name: str, hash: int = -1, threads: int = -1):
        if service := self._get_service(engine_name):
            if hash > 0:
                service.update_settings(hash_size=hash)
            if threads > 0:
                service.update_settings(threads=threads)
            service.set_options()

    def go(self, engine_name: str):
        """Executes a search using the constraints stored in the engine's settings."""
        if service := self._get_service(engine_name):
            service.go()

    def go_depth(self, engine_name: str, depth: int):
        if service := self._get_service(engine_name):
            service.go_depth(depth)

    def go_infinite(self, engine_name: str):
        if service := self._get_service(engine_name):
            service.go_infinite()

    def go_time(self, engine_name: str, ms: int):
        if service := self._get_service(engine_name):
            service.go_time(ms)

    def go_nodes(self, engine_name: str, nodes: int):
        if service := self._get_service(engine_name):
            service.go_nodes(nodes)

    def stop_search(self, engine_name: str):
        if service := self._get_service(engine_name):
            service.stop_search()

    def asdict(self, engine_name: str) -> dict | None:
        if service := self._get_service(engine_name):
            return service.status.asdict()
        return None

    def load_settings(self, engines_dict: dict):
        for engine_name, engine_data in engines_dict.items():
            self.create_engine(engine_name)

            if "settings" in engine_data:
                self.update_settings(engine_name, **engine_data["settings"])

    def get_export_state(self) -> dict:
        state = {}
        for name in self.engines_model.active_engines:
            engine_dict = self.asdict(name)
            if engine_dict:
                state[name] = engine_dict
        return state
