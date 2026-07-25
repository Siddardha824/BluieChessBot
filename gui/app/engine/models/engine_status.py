"""Engine status structural aggregation model.

This module provides the EngineStatus class, which groups the metadata,
configuration settings, and search telemetry for a chess engine session.
"""

from PySide6.QtCore import QObject
from .engine_info import EngineInfo
from .analysis_state import AnalysisState
from .engine_settings import EngineSettings


class EngineStatus(QObject):
    """Aggregate metadata, settings, and live search metrics for an engine session.

    This structural model groups the engine identification info, settings, and live
    telemetry to represent a single active engine session.
    """

    def __init__(self, parent):
        """Initialize the engine status model.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self._info = EngineInfo(self)
        self._settings = EngineSettings(self)
        self._analysis = AnalysisState(self)

    @property
    def info(self) -> EngineInfo:
        """Return the engine metadata and process status."""
        return self._info

    @property
    def settings(self) -> EngineSettings:
        """Return the user-configurable search constraints and parameters."""
        return self._settings

    @property
    def analysis(self) -> AnalysisState:
        """Return the live search statistics and evaluation metrics."""
        return self._analysis

    def asdict(self) -> dict:
        """Convert the engine status model to a dictionary.

        Returns:
            A dictionary containing the engine info and settings.
        """
        return {
            "info": self.info.asdict(),
            "settings": self.settings.asdict(),
        }