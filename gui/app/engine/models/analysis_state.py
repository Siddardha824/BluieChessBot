"""Engine analysis state model for search telemetry.

This module provides the AnalysisState class, which tracks and exposes
the evaluation score, search depth, PV (principal variation) lines, and
other search telemetry emitted by the chess engine subprocess.
"""

from PySide6.QtCore import QObject, Signal
from typing import List, Optional


class AnalysisState(QObject):
    """Manage the active search statistics and evaluation metrics of the engine.

    This model stores depth, node counts, nps, search time, score evaluation,
    is_mate, mate_in, principal variation (PV), and best calculated move.
    """

    analysis_state_changed = Signal()

    def __init__(self, parent):
        """Initialize the engine analysis state model.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self._depth: int = 0
        self._nps: int = 0
        self._nodes: int = 0
        self._time_ms: int = 0
        self._score: float = 0.0
        self._is_mate: bool = False
        self._mate_in: Optional[int] = None
        self._pv: List[str] = []
        self._best_move: Optional[str] = None

    # Properties silently update internal state to prevent signal storms
    @property
    def depth(self) -> int:
        """Return the current search depth in plies."""
        return self._depth

    @depth.setter
    def depth(self, val: int):
        """Set the search depth in plies."""
        self._depth = val

    @property
    def nps(self) -> int:
        """Return the current search speed in nodes per second (NPS)."""
        return self._nps

    @nps.setter
    def nps(self, val: int):
        """Set the search speed in nodes per second."""
        self._nps = val

    @property
    def nodes(self) -> int:
        """Return the total number of nodes evaluated during search."""
        return self._nodes

    @nodes.setter
    def nodes(self, val: int):
        """Set the total nodes evaluated."""
        self._nodes = val

    @property
    def time_ms(self) -> int:
        """Return the total elapsed search time in milliseconds."""
        return self._time_ms

    @time_ms.setter
    def time_ms(self, val: int):
        """Set the search time in milliseconds."""
        self._time_ms = val

    @property
    def score(self) -> float:
        """Return the search evaluation score (centipawns or mate indicator)."""
        return self._score

    @score.setter
    def score(self, val: float):
        """Set the search evaluation score."""
        self._score = val

    @property
    def is_mate(self) -> bool:
        """Return True if a checkmate has been found in the search tree."""
        return self._is_mate

    @is_mate.setter
    def is_mate(self, val: bool):
        """Set checkmate discovery status."""
        self._is_mate = val

    @property
    def mate_in(self) -> Optional[int]:
        """Return the number of moves to checkmate, or None if no mate found."""
        return self._mate_in

    @mate_in.setter
    def mate_in(self, val: Optional[int]):
        """Set moves to checkmate."""
        self._mate_in = val

    @property
    def pv(self) -> List[str]:
        """Return the principal variation (PV) move sequence as UCI strings."""
        return self._pv

    @pv.setter
    def pv(self, val: List[str]):
        """Set the principal variation (PV) move list."""
        self._pv = val

    @property
    def best_move(self) -> Optional[str]:
        """Return the best move coordinate string calculated by the engine."""
        return self._best_move

    @best_move.setter
    def best_move(self, val: Optional[str]):
        """Set the best move coordinate string."""
        self._best_move = val

    def notify_updated(self):
        """Emit the analysis_state_changed signal to notify listeners.

        Should be called manually by the engine service once a full data
        batch is parsed to trigger UI updates.
        """
        self.analysis_state_changed.emit()

    def reset(self):
        """Clear all telemetry and evaluation metrics to starting/idle values."""
        self._depth = 0
        self._nps = 0
        self._nodes = 0
        self._time_ms = 0
        self._score = 0.0
        self._is_mate = False
        self._mate_in = None
        self._pv = []
        self._best_move = None
        self.notify_updated()