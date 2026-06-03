from __future__ import annotations

from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.analysis_state import AnalysisState

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
    """

    @staticmethod
    def parse_line(
        line: str,
        state : "AnalysisState",
        is_white_turn: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Parses a single UCI output line.
        """

        line = line.strip()

        if not line:
            return None

        tokens = line.split()
        cmd = tokens[0]

        if cmd == "uciok":
            return {"type": PacketType.UCIOK}

        if cmd == "readyok":
            return {"type": PacketType.READYOK}

        if cmd == "bestmove":
            return UCIParser._parse_bestmove(tokens)

        if cmd == "id":
            return UCIParser._parse_id(tokens)

        if cmd == "info":
            return {
                "type": PacketType.INFO,
                "state": UCIParser._parse_info(
                    tokens,
                    state,
                    is_white_turn
                )
            }

        return None

    @staticmethod
    def _parse_bestmove(
        tokens: List[str]
    ) -> Dict[str, Any]:

        best_move = tokens[1] if len(tokens) > 1 else None

        ponder = None

        if len(tokens) > 3 and tokens[2] == "ponder":
            ponder = tokens[3]

        return {
            "type": PacketType.BESTMOVE,
            "best_move": best_move,
            "ponder": ponder
        }

    @staticmethod
    def _parse_id(
        tokens: List[str]
    ) -> Optional[Dict[str, Any]]:

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
    ) -> AnalysisState:

        i = 1
        n = len(tokens)

        while i < n:

            token = tokens[i]

            if token == "depth":
                i = UCIParser._parse_int_field(
                    state,
                    tokens,
                    i,
                    "depth"
                )

            elif token == "nodes":
                i = UCIParser._parse_int_field(
                    state,
                    tokens,
                    i,
                    "nodes"
                )

            elif token == "nps":
                i = UCIParser._parse_int_field(
                    state,
                    tokens,
                    i,
                    "nps"
                )

            elif token == "time":
                i = UCIParser._parse_int_field(
                    state,
                    tokens,
                    i,
                    "time_ms"
                )

            elif token == "score":
                i = UCIParser._parse_score(
                    state,
                    tokens,
                    i,
                    is_white_turn
                )

            elif token == "pv":
                UCIParser._parse_pv(
                    state,
                    tokens,
                    i
                )
                break

            else:
                i += 1

        return state

    @staticmethod
    def _parse_int_field(
        state: AnalysisState,
        tokens: List[str],
        index: int,
        attribute: str
    ) -> int:

        if index + 1 >= len(tokens):
            return index + 1

        try:
            setattr(
                state,
                attribute,
                int(tokens[index + 1])
            )
        except ValueError:
            pass

        return index + 2

    @staticmethod
    def _parse_score(
        state: AnalysisState,
        tokens: List[str],
        index: int,
        is_white_turn: bool
    ) -> int:

        if index + 2 >= len(tokens):
            return index + 1

        score_type = tokens[index + 1]
        score_str = tokens[index + 2]

        try:

            score_value = int(score_str)

            if score_type == "cp":

                score = score_value / 100.0

                if not is_white_turn:
                    score = -score

                state.score = score
                state.is_mate = False

            elif score_type == "mate":

                mate_value = score_value

                if not is_white_turn:
                    mate_value = -mate_value

                state.is_mate = True
                state.mate_in = mate_value

                state.score = (
                    999.0
                    if mate_value > 0
                    else -999.0
                )

        except ValueError:
            pass

        index += 3

        if (
            index < len(tokens)
            and tokens[index] in (
                "upperbound",
                "lowerbound"
            )
        ):
            index += 1

        return index

    @staticmethod
    def _parse_pv(
        state: AnalysisState,
        tokens: List[str],
        index: int
    ) -> None:

        state.pv = tokens[index + 1:]
