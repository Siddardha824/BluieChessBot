from PySide6.QtCore import QObject, Signal
from gui.utils import get_logger


logger = get_logger(__name__)

class EngineInfo(QObject):
    """
    Reactive data model representing the current metadata, capabilities,
    and runtime configuration status of the active UCI chess engine subprocess.
    """
    name_changed = Signal(str)
    author_changed = Signal(str)
    status_changed = Signal(str)
    hash_size_changed = Signal(int)
    threads_changed = Signal(int)
    path_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = "Awaiting Handshake..."
        self._author = ""
        self._hash_size = 0
        self._threads = 1
        self._status = "Disconnected"
        self._connection_status = "Disconnected"
        self._path = ""

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        if self._name != val:
            logger.debug("Engine name changed: %s", val)
            self._name = val
            self.name_changed.emit(self._name)

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, val: str):
        if self._author != val:
            logger.debug("Engine author changed: %s", val)
            self._author = val
            self.author_changed.emit(self._author)

    @property
    def hash_size(self) -> int:
        return self._hash_size

    @hash_size.setter
    def hash_size(self, val: int):
        if self._hash_size != val:
            logger.debug("Engine hash size changed: %s", val)
            self._hash_size = val
            self.hash_size_changed.emit(self._hash_size)

    @property
    def threads(self) -> int:
        return self._threads

    @threads.setter
    def threads(self, val: int):
        if self._threads != val:
            logger.debug("Engine threads changed: %s", val)
            self._threads = val
            self.threads_changed.emit(self._threads)

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, val: str):
        if self._status != val:
            logger.debug("Engine status changed: %s", val)
            self._status = val
            self.status_changed.emit(self._status)

    @property
    def connection_status(self) -> str:
        return self._connection_status

    @connection_status.setter
    def connection_status(self, val: str):
        if self._connection_status != val:
            logger.info("Engine connection status changed: %s", val)
            self._connection_status = val
            self.status_changed.emit(self._connection_status)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, val: str):
        if self._path != val:
            logger.debug("Engine path changed: %s", val)
            self._path = val
            self.path_changed.emit(self._path)
