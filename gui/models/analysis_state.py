# gui/models/analysis_state.py

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AnalysisState:
    """
    Data container representing the active search statistics and evaluation
    metrics of the C++ UCI engine.
    """
    depth: int = 0
    nps: int = 0
    nodes: int = 0
    time_ms: int = 0
    
    # Evaluation metrics
    # score represents the centipawn score from White's perspective.
    # Positive values mean White is advantaged; negative values mean Black is advantaged.
    score: float = 0.0
    is_mate: bool = False
    mate_in: Optional[int] = None
    
    # Principal Variation (list of move coordinate strings, e.g. ["e2e4", "e7e5"])
    pv: List[str] = field(default_factory=list)
    
    # Best calculated move coordinate string once complete (e.g. "e2e4")
    best_move: Optional[str] = None
