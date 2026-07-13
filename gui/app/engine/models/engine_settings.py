from PySide6.QtCore import QObject
import inspect

class EngineSettings(QObject):
    """
    Data model representing search constraints and engine configuration
    inputted by the UI to be passed to the engine service.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self._constraint_mode: str = "depth"
        self._max_depth: int = 3
        self._max_time_ms: int = 1000
        self._max_nodes: int = 10000
        self._hash_size: int = 64
        self._threads: int = 1
        self._engine_path: str = ""

    @property
    def constraint_mode(self) -> str: return self._constraint_mode

    @constraint_mode.setter
    def constraint_mode(self, val: str):
        if val.lower() in ["depth", "time", "nodes", "infinite"]:
            self._constraint_mode = val.lower()
        else:
            raise ValueError(f"Invalid constraint mode: {val}. Must be one of: depth, time, nodes, infinite.")

    @property
    def max_depth(self) -> int: return self._max_depth

    @max_depth.setter
    def max_depth(self, val: int):
        if val < 1:
            raise ValueError("Max depth must be a positive integer.")
        self._max_depth = val

    @property
    def max_time_ms(self) -> int: return self._max_time_ms

    @max_time_ms.setter
    def max_time_ms(self, val: int):
        if val < 1:
            raise ValueError("Max time (ms) must be a positive integer.")
        self._max_time_ms = val

    @property
    def max_nodes(self) -> int: return self._max_nodes

    @max_nodes.setter
    def max_nodes(self, val: int):
        if val < 1:
            raise ValueError("Max nodes must be a positive integer.")
        self._max_nodes = val

    @property
    def hash_size(self) -> int:
        return self._hash_size
    
    @hash_size.setter
    def hash_size(self, val: int):
        if val < 1:
            raise ValueError("Hash size should be positive integer.")
        self._hash_size = val

    @property
    def threads(self) -> int:
        return self._threads
    
    @threads.setter
    def threads(self, val: int):
        if val < 1:
            raise ValueError("No of Threads should be a positive integer.")
        self._threads = val

    @property
    def engine_path(self) -> str: return self._engine_path

    @engine_path.setter
    def engine_path(self, val: str):
        if not isinstance(val, str):
            raise ValueError("Engine path must be a string.")
        self._engine_path = val

    def asdict(self) -> dict:
        properties = [
            name for name, val in inspect.getmembers(type(self), lambda v: isinstance(v, property))
        ]

        return {
            key: getattr(self, key) for key in properties
        }