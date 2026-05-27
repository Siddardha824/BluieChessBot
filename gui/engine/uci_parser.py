# gui/engine/uci_parser.py

from typing import Dict, Any, List, Optional
from gui.models.analysis_state import AnalysisState
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class UCIParser:
    """
    Stateless parser designed to translate standard UCI protocol stdout streams
    from the C++ engine into structured Python dictionary actions and AnalysisState models.
    """
    
    @staticmethod
    def parse_line(line: str, is_white_turn: bool = True) -> Optional[Dict[str, Any]]:
        """
        Parses a single line of standard output from the UCI engine.
        
        Args:
            line: The raw stdout string line from the engine.
            is_white_turn: Current turn on the board. Used to normalize score perspective.
            
        Returns:
            A dictionary containing the parsed packet type and data, or None if unrecognized.
            Possible outputs:
            - {"type": "uciok"}
            - {"type": "readyok"}
            - {"type": "bestmove", "best_move": "e2e4"}
            - {"type": "info", "state": AnalysisState}
            - {"type": "id", "name": "...", "author": "..."}
        """
        line = line.strip()
        if not line:
            return None
            
        tokens = line.split()
        cmd = tokens[0]
        
        if cmd == "uciok":
            return {"type": "uciok"}
            
        elif cmd == "readyok":
            return {"type": "readyok"}
            
        elif cmd == "bestmove":
            best_move = tokens[1] if len(tokens) > 1 else None
            ponder = None
            if len(tokens) > 3 and tokens[2] == "ponder":
                ponder = tokens[3]
            return {
                "type": "bestmove",
                "best_move": best_move,
                "ponder": ponder
            }
            
        elif cmd == "id":
            if len(tokens) >= 3:
                id_type = tokens[1]
                id_val = " ".join(tokens[2:])
                return {"type": "id", id_type: id_val}
                
        elif cmd == "info":
            return {
                "type": "info",
                "state": UCIParser._parse_info(tokens, is_white_turn)
            }
            
        return None

    @staticmethod
    def _parse_info(tokens: List[str], is_white_turn: bool) -> AnalysisState:
        """
        Helper to parse the flat UCI info command tokens into an AnalysisState model.
        """
        state = AnalysisState()
        n = len(tokens)
        
        i = 1
        while i < n:
            token = tokens[i]
            
            if token == "depth" and i + 1 < n:
                try:
                    state.depth = int(tokens[i + 1])
                except ValueError:
                    pass
                i += 2
                
            elif token == "nps" and i + 1 < n:
                try:
                    state.nps = int(tokens[i + 1])
                except ValueError:
                    pass
                i += 2
                
            elif token == "nodes" and i + 1 < n:
                try:
                    state.nodes = int(tokens[i + 1])
                except ValueError:
                    pass
                i += 2
                
            elif token == "time" and i + 1 < n:
                try:
                    state.time_ms = int(tokens[i + 1])
                except ValueError:
                    pass
                i += 2
                
            elif token == "score" and i + 2 < n:
                score_type = tokens[i + 1]  # "cp" or "mate"
                score_str = tokens[i + 2]
                
                try:
                    score_val = int(score_str)
                    
                    if score_type == "cp":
                        # Standard centipawn score from active player's perspective
                        # Convert to centipawns as floating point (e.g. 15 -> 0.15)
                        score_float = score_val / 100.0
                        
                        # Normalize to White's perspective:
                        # If Black's turn and score is +1.00 (Black is winning), then score from White is -1.00.
                        if not is_white_turn:
                            score_float = -score_float
                            
                        state.score = score_float
                        state.is_mate = False
                        
                    elif score_type == "mate":
                        state.is_mate = True
                        
                        # Normalize mate perspective to White's side:
                        # If Black's turn, a mate in +2 (Black mates White in 2) means White is mated in 2 (-2).
                        mate_val = score_val
                        if not is_white_turn:
                            mate_val = -mate_val
                            
                        state.mate_in = mate_val
                        # For display advantage, mate is represented as a high/low score value
                        state.score = 999.0 if mate_val > 0 else -999.0
                        
                except ValueError:
                    pass
                
                # Advance past score cp/mate <val>
                i += 3
                # Skip optional bound tokens (e.g. upperbound, lowerbound)
                if i < n and tokens[i] in ("upperbound", "lowerbound"):
                    i += 1
                    
            elif token == "pv":
                # The principal variation contains all subsequent tokens up to the end
                state.pv = tokens[i + 1:]
                break
                
            else:
                # Unhandled info key, move forward
                i += 1
                
        return state
