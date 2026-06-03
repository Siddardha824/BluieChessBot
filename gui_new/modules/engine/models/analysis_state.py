from PySide6.QtCore import QObject, Signal
from typing import List, Optional

class AnalysisState(QObject):
    """
    Reactive Data Model representing the active search statistics and evaluation
    metrics of the C++ UCI engine.
    """

    updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Current engine search state
        self._depth: int = 0
        self._nps: int = 0
        self._nodes: int = 0
        self._time_ms: int = 0

        # Evaluation metrics
        self._score: float = 0.0
        self._is_mate: bool = False
        self._mate_in: Optional[int] = None
        
        # Principal Variation
        self._pv: List[str] = []
        
        self._best_move: Optional[str] = None

    @property
    def depth(self) -> int:
        return self._depth
    
    @depth.setter
    def depth(self, val: int):
        self._depth = val

    @property
    def nps(self) -> int:
        return self._nps
    
    @nps.setter
    def nps(self, val: int):
        self._nps = val

    @property
    def nodes(self) -> int:
        return self._nodes
    
    @nodes.setter
    def nodes(self, val: int):
        self._nodes = val

    @property
    def time_ms(self) -> int:
        return self._time_ms
    
    @time_ms.setter
    def time_ms(self, val: int):
        self._time_ms = val

    @property
    def score(self) -> float:
        return self._score
    
    @score.setter
    def score(self, val: float):
        self._score = val

    @property
    def is_mate(self) -> bool:
        return self._is_mate
    
    @is_mate.setter
    def is_mate(self, val: bool):
        self._is_mate = val
    
    @property
    def mate_in(self) -> Optional[int]:
        return self._mate_in
    
    @mate_in.setter
    def mate_in(self, val: Optional[int]):
        self._mate_in = val

    @property
    def pv(self) -> List[str]:
        return self._pv
    
    @pv.setter
    def pv(self, val: List[str]):
        self._pv = val

    @property
    def best_move(self) -> Optional[str]:
        return self._best_move
    
    @best_move.setter
    def best_move(self, val: Optional[str]):
        self._best_move = val
