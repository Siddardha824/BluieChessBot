"""Parse Universal Chess Interface (UCI) protocol messages from chess engines.

This module provides parsing utilities for the Universal Chess Interface (UCI) protocol.
It translates standard UCI protocol output from chess engines into structured packets
and AnalysisState models for use in the GUI application.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from gui.utils import get_logger

if TYPE_CHECKING:
    from ..models.analysis_state import AnalysisState

logger = get_logger(__name__)


class PacketType:
    """Define constants representing different UCI protocol packet types."""

    UCIOK = "uciok"          # Engine is ready and initialized
    READYOK = "readyok"      # Engine is ready for input
    BESTMOVE = "bestmove"    # Engine has found the best move
    INFO = "info"            # Analysis information (depth, score, etc.)
    ID = "id"                # Engine identification (name, author)


class UCIParser:
    """Provide a stateless UCI protocol parser for chess engine communication.

    This parser translates standard UCI protocol stdout streams from chess engines
    into structured packets and AnalysisState models. It uses Python 3.10+ pattern matching
    for high-performance string parsing.

    Design Principles:
    - Stateless: No internal state between parse calls.
    - Efficient: Optimized for high-throughput parsing with minimal allocations.
    - Robust: Gracefully handles malformed or partial input.
    """

    @staticmethod
    def parse_line(
        line: str,
        state: "AnalysisState",
        is_white_turn: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Parse a single line of UCI protocol output.

        Args:
            line: Raw output line from the chess engine.
            state: Current analysis state to update with parsed information.
            is_white_turn: Whether it's currently white's turn (affects score sign).

        Returns:
            A dictionary containing parsed packet data, or None if the line is
            empty or unrecognized.
        """
        line = line.strip()
        if not line:
            return None

        tokens = line.split()
        if not tokens:
            return None

        cmd = tokens[0]

        # Pattern match on UCI command type
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
        """Parse a UCI 'bestmove' command.

        Format: bestmove <move> [ponder <move>]

        Args:
            tokens: List of tokens from the UCI output line.

        Returns:
            A dictionary containing "type", "best_move", and optional "ponder".
        """
        best_move = tokens[1] if len(tokens) > 1 else None
        ponder = tokens[3] if len(tokens) > 3 and tokens[2] == "ponder" else None
        return {
            "type": PacketType.BESTMOVE,
            "best_move": best_move,
            "ponder": ponder
        }

    @staticmethod
    def _parse_id(tokens: List[str]) -> Optional[Dict[str, Any]]:
        """Parse a UCI 'id' command for engine identification.

        Format: id name <engine name> | id author <author name>

        Args:
            tokens: List of tokens from the UCI output line.

        Returns:
            A dictionary with id_type as the key and id_value as the value,
            or None if the command is malformed.
        """
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
        """Parse a UCI 'info' command and update the analysis state.

        The info command contains analysis parameters like depth, nodes searched,
        score, and principal variation (best line found so far).

        UCI Score Convention:
        - Score in centipawns (cp): 1 = 0.01 pawns (relative to perspective).
        - Score in mate (mate): Number of moves to checkmate.
        - Scores from engine perspective always favor white; we adjust for black.

        Args:
            tokens: List of tokens from the UCI output line (after 'info').
            state: AnalysisState object to update in-place.
            is_white_turn: Whether it's white's turn (needed to adjust score sign).

        Returns:
            The updated AnalysisState object.
        """
        it = iter(tokens[1:])

        try:
            for token in it:
                match token:
                    case "depth":
                        # Search depth reached in this analysis iteration
                        state.depth = int(next(it))
                    case "nodes":
                        # Total nodes evaluated so far
                        state.nodes = int(next(it))
                    case "nps":
                        # Nodes per second (search speed indicator)
                        state.nps = int(next(it))
                    case "time":
                        # Time elapsed in milliseconds
                        state.time_ms = int(next(it))
                    case "score":
                        # Parse engine evaluation score
                        score_type = next(it)
                        score_val = int(next(it))

                        if score_type == "cp":
                            # Convert centipawns to pawns and adjust for perspective
                            score = score_val / 100.0
                            state.score = score if is_white_turn else -score
                            state.is_mate = False

                        elif score_type == "mate":
                            # Mate score: positive = we win, negative = we lose
                            mate_val = score_val if is_white_turn else -score_val
                            state.is_mate = True
                            state.mate_in = mate_val
                            # Store extreme score to indicate mate advantage
                            state.score = 999.0 if mate_val > 0 else -999.0

                    case "pv":
                        # Principal variation: best line of play found
                        # Consume all remaining tokens as the principal variation moves
                        state.pv = list(it)
                        break

        except (StopIteration, ValueError):
            # StopIteration: Line ended abruptly (e.g., 'depth' with no value)
            # ValueError: Integer conversion failed (malformed number)
            # Gracefully handle and continue with partially parsed state
            pass

        return state