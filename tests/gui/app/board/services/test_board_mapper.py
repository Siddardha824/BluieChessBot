import pytest
import chess
from gui.app.board.services.board_mapper import BoardMapper

class TestBoardMapper:
    """Test suite for the BoardMapper static methods."""

    @pytest.mark.parametrize(
        "ui_index, expected_coord, expected_chess_square",
        [
            # Corners
            (0, "a8", chess.A8),   # Top-Left
            (7, "h8", chess.H8),   # Top-Right
            (56, "a1", chess.A1),  # Bottom-Left
            (63, "h1", chess.H1),  # Bottom-Right
            
            # Centers
            (27, "d5", chess.D5),
            (28, "e5", chess.E5),
            (35, "d4", chess.D4),
            (36, "e4", chess.E4),
        ]
    )
    def test_valid_board_mappings(self, ui_index, expected_coord, expected_chess_square):
        """Verify that UI indices map perfectly to coordinates and python-chess squares."""
        
        # Test index -> coord
        assert BoardMapper.index_to_coord(ui_index) == expected_coord
        
        # Test index -> square
        assert BoardMapper.index_to_square(ui_index) == expected_chess_square
        
        # Test coord -> index (Inverse)
        assert BoardMapper.coord_to_index(expected_coord) == ui_index

    @pytest.mark.parametrize(
        "invalid_coord",
        [
            "a9",  # Rank too high
            "i1",  # File out of bounds
            "z99", # Complete nonsense
            "",    # Empty string
        ]
    )
    def test_coord_to_index_invalid_inputs(self, invalid_coord):
        """Verify that passing invalid coordinate strings raises the appropriate ValueError from python-chess."""
        with pytest.raises(ValueError):
            BoardMapper.coord_to_index(invalid_coord)