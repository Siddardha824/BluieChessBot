import pytest
from gui.app.engine.services.uci_parser import UCIParser, PacketType
from gui.app.engine.models.analysis_state import AnalysisState


class TestUCIParser:
    """Test suite for the stateless UCIParser utility class."""

    @pytest.fixture
    def analysis_state(self):
        """Fixture to provide a fresh, isolated AnalysisState model."""
        return AnalysisState(parent=None)

    # --- Basic Command Tests ---

    @pytest.mark.parametrize(
        "line, expected_packet",
        [
            ("uciok", {"type": PacketType.UCIOK}),
            ("readyok", {"type": PacketType.READYOK}),
            ("  uciok  ", {"type": PacketType.UCIOK}),  # Trimming leading/trailing whitespace
            ("", None),                               # Empty string
            ("   ", None),                            # Whitespace only
            ("unrecognized_command arg1 arg2", None),  # Unrecognized command
        ]
    )
    def test_basic_commands(self, line, expected_packet, analysis_state):
        """Verify parsing of simple status commands and invalid inputs."""
        result = UCIParser.parse_line(line, analysis_state)
        assert result == expected_packet

    # --- ID Command Tests ---

    @pytest.mark.parametrize(
        "line, expected_packet",
        [
            ("id name Stockfish 16", {"type": PacketType.ID, "name": "Stockfish 16"}),
            ("id author The Stockfish Developers", {"type": PacketType.ID, "author": "The Stockfish Developers"}),
            ("id name Multi-word Name", {"type": PacketType.ID, "name": "Multi-word Name"}),
            ("id", None),                  # Malformed ID command (too few tokens)
            ("id name", None),             # Malformed ID command (no value)
        ]
    )
    def test_id_command(self, line, expected_packet, analysis_state):
        """Verify parsing of id command variants for engine identification."""
        result = UCIParser.parse_line(line, analysis_state)
        assert result == expected_packet

    # --- Bestmove Command Tests ---

    @pytest.mark.parametrize(
        "line, expected_packet",
        [
            ("bestmove e2e4", {"type": PacketType.BESTMOVE, "best_move": "e2e4", "ponder": None}),
            ("bestmove e2e4 ponder e7e5", {"type": PacketType.BESTMOVE, "best_move": "e2e4", "ponder": "e7e5"}),
            ("bestmove (none)", {"type": PacketType.BESTMOVE, "best_move": "(none)", "ponder": None}),
            ("bestmove", {"type": PacketType.BESTMOVE, "best_move": None, "ponder": None}),
        ]
    )
    def test_bestmove_command(self, line, expected_packet, analysis_state):
        """Verify parsing of bestmove commands with or without ponder moves."""
        result = UCIParser.parse_line(line, analysis_state)
        assert result == expected_packet

    # --- Info Command (Telemetry) Tests ---

    def test_parse_info_telemetry(self, analysis_state):
        """Verify that basic search telemetry fields are parsed and stored in the AnalysisState."""
        line = "info depth 12 nodes 123456 nps 98765 time 1234 pv e2e4 e7e5 g1f3"
        result = UCIParser.parse_line(line, analysis_state)
        
        assert result is not None
        assert result["type"] == PacketType.INFO
        
        state = result["state"]
        assert state == analysis_state
        assert state.depth == 12
        assert state.nodes == 123456
        assert state.nps == 98765
        assert state.time_ms == 1234
        assert state.pv == ["e2e4", "e7e5", "g1f3"]

    # --- Info Command (Score & Mate) Tests ---

    @pytest.mark.parametrize(
        "line, is_white_turn, expected_score, expected_is_mate, expected_mate_in",
        [
            # Centipawns - White's perspective
            ("info score cp 125", True, 1.25, False, None),
            ("info score cp -50", True, -0.50, False, None),
            
            # Centipawns - Black's perspective (perspective inversion)
            ("info score cp 125", False, -1.25, False, None),
            ("info score cp -50", False, 0.50, False, None),
            
            # Mate - White's perspective
            ("info score mate 3", True, 999.0, True, 3),
            ("info score mate -5", True, -999.0, True, -5),
            
            # Mate - Black's perspective (perspective inversion)
            ("info score mate 3", False, -999.0, True, -3),
            ("info score mate -5", False, 999.0, True, 5),
        ]
    )
    def test_parse_info_scores(self, line, is_white_turn, expected_score, expected_is_mate, expected_mate_in, analysis_state):
        """Verify that engine score evaluations and mates are correctly parsed and inverted based on active side's turn."""
        result = UCIParser.parse_line(line, analysis_state, is_white_turn=is_white_turn)
        assert result is not None
        
        state = result["state"]
        assert state.score == expected_score
        assert state.is_mate == expected_is_mate
        assert state.mate_in == expected_mate_in

    # --- Info Command Error Handling Tests ---

    @pytest.mark.parametrize(
        "malformed_line",
        [
            "info depth abc",              # ValueError: integer conversion fails
            "info nodes",                  # StopIteration: value missing at end of line
            "info nps xyz time 100",       # Mix of invalid and valid tokens
            "info score cp",               # StopIteration: score value missing
            "info score mate",             # StopIteration: mate value missing
            "info score invalid_type 12",  # Unrecognized score type (no state update)
        ]
    )
    def test_parse_info_error_handling(self, malformed_line, analysis_state):
        """Verify that malformed or incomplete info tokens do not raise crashes but fail gracefully."""
        # This shouldn't raise ValueError or StopIteration
        result = UCIParser.parse_line(malformed_line, analysis_state)
        assert result is not None
        assert result["type"] == PacketType.INFO
        assert isinstance(result["state"], AnalysisState)
