from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from gui.utils import get_logger

if TYPE_CHECKING:
    from ..models.analysis_state import AnalysisState

logger = get_logger(__name__)

class PacketType:
    UCIOK = "uciok"
    READYOK = "readyok"
    BESTMOVE = "bestmove"
    INFO = "info"
    ID = "id"

class UCIParser:
    """
    Stateless parser designed to translate standard UCI protocol stdout streams
    from the chess engine into structured packets and AnalysisState models.
    Optimized for high-throughput string parsing.
    """
    
    @staticmethod
    def parse_line(
        line: str,
        state: "AnalysisState",
        is_white_turn: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Parses a single UCI output line using Python 3.10+ optimized match jump tables.
        """
        line = line.strip()
        if not line:
            return None

        tokens = line.split()
        if not tokens:
            return None

        cmd = tokens[0]

        match cmd:
            case "info":
                return {
                    "type": PacketType.INFO,
                    "state": UCIParser._parse_info(tokens, state, is_white_turn)
                }
            case "bestmove":
                return UCIParser._parse_bestmove(tokens)
            case "uciok":
                return {"type": PacketType.UCIOK}
            case "readyok":
                return {"type": PacketType.READYOK}
            case "id":
                return UCIParser._parse_id(tokens)
            case _:
                # Ignore unrecognized/spammy UCI commands gracefully
                return None

    @staticmethod
    def _parse_bestmove(tokens: List[str]) -> Dict[str, Any]:
        best_move = tokens[1] if len(tokens) > 1 else None
        ponder = tokens[3] if len(tokens) > 3 and tokens[2] == "ponder" else None
        return {
            "type": PacketType.BESTMOVE,
            "best_move": best_move,
            "ponder": ponder
        }

    @staticmethod
    def _parse_id(tokens: List[str]) -> Optional[Dict[str, Any]]:
        if len(tokens) < 3:
            return None
            
        id_type = tokens[1]
        id_value = " ".join(tokens[2:])
        return {
            "type": PacketType.ID,
            id_type: id_value
        }

    @staticmethod
    def _parse_info(
        tokens: List[str],
        state: "AnalysisState",
        is_white_turn: bool
    ) -> "AnalysisState":
        """
        Iterates over the info string chunks. 
        Uses iter() for zero-copy traversal, avoiding manual index lookups.
        """
        it = iter(tokens[1:])
        
        try:
            for token in it:
                match token:
                    case "depth":
                        state.depth = int(next(it))
                    case "nodes":
                        state.nodes = int(next(it))
                    case "nps":
                        state.nps = int(next(it))
                    case "time":
                        state.time_ms = int(next(it))
                    case "score":
                        score_type = next(it)
                        score_val = int(next(it))
                        
                        if score_type == "cp":
                            score = score_val / 100.0
                            state.score = score if is_white_turn else -score
                            state.is_mate = False
                            
                        elif score_type == "mate":
                            mate_val = score_val if is_white_turn else -score_val
                            state.is_mate = True
                            state.mate_in = mate_val
                            state.score = 999.0 if mate_val > 0 else -999.0
                            
                    case "pv":
                        # Instantly consume all remaining tokens into the PV list
                        state.pv = list(it)
                        break
                        
        except (StopIteration, ValueError):
            # StopIteration: The line ended abruptly before a value was found (e.g., 'depth' followed by nothing)
            # ValueError: A cast to int() failed
            # In either case, we safely catch it and move on, updating whatever was valid
            pass
            
        return state