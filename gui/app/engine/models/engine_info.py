from PySide6.QtCore import QObject, Signal

class EngineInfo(QObject):
    """
    Data model representing the current metadata, capabilities,
    and runtime configuration status of the active UCI chess engine subprocess.
    """
    info_updated = Signal()

    def __init__(self, parent=None, name="", author="", hash_size=0, threads=0, path=""):
        super().__init__(parent)
        self._name = name
        self._author = author
        self._hash_size = hash_size
        self._threads = threads
        self._connection_status = "NotRunning"
        self._search_status = "Offline"

    # Properties silently update internal state to prevent signal storms
    @property
    def name(self) -> str: return self._name
    
    @name.setter
    def name(self, val: str): self._name = val

    @property
    def author(self) -> str: return self._author
    
    @author.setter
    def author(self, val: str): self._author = val

    @property
    def hash_size(self) -> int: return self._hash_size
    
    @hash_size.setter
    def hash_size(self, val: int): self._hash_size = val

    @property
    def threads(self) -> int: return self._threads
    
    @threads.setter
    def threads(self, val: int): self._threads = val

    @property
    def connection_status(self) -> str: return self._connection_status
    
    @connection_status.setter
    def connection_status(self, val: str): self._connection_status = val

    @property
    def search_status(self) -> str: return self._search_status
    
    @search_status.setter
    def search_status(self, val: str): self._search_status = val

    def notify_updated(self):
        """Called manually by the service once a full data batch is parsed."""
        self.info_updated.emit()