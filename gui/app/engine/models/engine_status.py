from PySide6.QtCore import QObject
from .engine_info import EngineInfo
from .analysis_state import AnalysisState
from .engine_settings import EngineSettings

class EngineStatus(QObject):
    """
    Aggregated structural model grouping metadata, settings, and live search metrics
    for a dedicated engine session.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self._info = EngineInfo(self)
        self._settings = EngineSettings(self)
        self._analysis = AnalysisState(self)

    @property
    def info(self) -> EngineInfo:
        return self._info

    @property
    def settings(self) -> EngineSettings:
        return self._settings

    @property
    def analysis(self) -> AnalysisState:
        return self._analysis
    
    def asdict(self) -> dict:
        return {
            "info": self.info.asdict(),
            "settings": self.settings.asdict(),
        }