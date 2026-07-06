from PySide6.QtCore import QObject, Signal
from .engine_status import EngineStatus
from gui.utils import get_logger

logger = get_logger(__name__)

class Engines(QObject):
    """
    Reactive data model which stores data of all the currently connected UCI chess engine subprocesses.
    """
    engine_added = Signal(str, object)
    engine_removed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_engines: dict[str, EngineStatus] = {}

    @property
    def active_engines(self) -> list[str]:
        return list(self._active_engines.keys())

    def get_engine(self, name: str) -> EngineStatus | None:
        return self._active_engines.get(name)

    def add_engine(self, name: str) -> EngineStatus | None:
        if not name:
            logger.warning("Cannot add an engine without a name")
            return None
        if name in self._active_engines:
            logger.warning("An engine with this name exists: %s", name)
            return self._active_engines[name]

        status = EngineStatus(self)
        self._active_engines[name] = status
        logger.info("Engine registered in model tree: %s", name)
        
        self.engine_added.emit(name, status)
        return status

    def remove_engine(self, name: str):
        engine = self._active_engines.pop(name, None)
        if engine is not None:
            logger.info("Engine removed from model tree: %s", name)
            engine.deleteLater()
            self.engine_removed.emit(name)

    def clear(self) -> None:
        for name in list(self._active_engines.keys()):
            self.remove_engine(name)