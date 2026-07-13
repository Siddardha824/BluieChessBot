from PySide6.QtCore import QObject, Signal
import inspect

class EngineInfo(QObject):
    """
    Data model representing the current metadata, capabilities,
    and runtime configuration status of the active UCI chess engine subprocess.
    """
    info_updated = Signal()

    def __init__(self, parent, name="", author=""):
        super().__init__(parent)
        self._name = name
        self._author = author
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

    def asdict(self) -> dict:
        properties = [
            name for name, val in inspect.getmembers(type(self), lambda v: isinstance(v, property))
        ]

        return {
            key: getattr(self, key) for key in properties
        }
