from PySide6.QtCore import QObject

class EngineSettings(QObject):
    """
    Data model representing search constraints and engine configuration
    inputted by the UI to be passed to the engine service.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.constraint_mode: str = "Depth"
        self.max_depth: int = 3
        self.max_time_ms: int = 1000
        self.max_nodes: int = 10000
        self.engine_path: str = ""