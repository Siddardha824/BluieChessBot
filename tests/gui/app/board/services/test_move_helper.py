import pytest
import chess
from unittest.mock import MagicMock
from gui.app.board.services.move_helper import MoveHelper


class TestMoveHelper:
    """Test suite for the MoveHelper utility class."""

    @pytest.fixture
    def mock_board_state(self):
        """Fixture to provide a mocked BoardState for interaction testing."""
        mock_board = MagicMock()
        return mock_board

    # --- make_move Tests ---

    def test_make_move_valid(self, mock_board_state):
        """Test that a valid, legal UCI move is applied to the board."""
        mock_board_state.is_legal.return_value = True
        
        result = MoveHelper.make_move(mock_board_state, "e2e4")
        
        assert result is True
        mock_board_state.is_legal.assert_called_once()
        mock_board_state.move.assert_called_once_with(chess.Move.from_uci("e2e4"))

    def test_make_move_invalid_uci_format(self, mock_board_state):
        """Test that an invalid UCI string format is caught and rejected."""
        result = MoveHelper.make_move(mock_board_state, "invalid_move")
        
        assert result is False
        mock_board_state.is_legal.assert_not_called()
        mock_board_state.move.assert_not_called()

    def test_make_move_illegal_on_board(self, mock_board_state):
        """Test that a structurally valid but contextually illegal move is rejected."""
        mock_board_state.is_legal.return_value = False
        
        # e2e5 is illegal from the starting position for a pawn
        result = MoveHelper.make_move(mock_board_state, "e2e5")
        
        assert result is False
        mock_board_state.is_legal.assert_called_once()
        mock_board_state.move.assert_not_called()

    # --- undo_move Tests ---

    def test_undo_move_success(self, mock_board_state):
        """Test that undoing a move successfully returns the undone UCI string."""
        mock_board_state.is_start_pos = False
        mock_board_state.undo.return_value = chess.Move.from_uci("e2e4")
        
        result = MoveHelper.undo_move(mock_board_state)
        
        assert result == "e2e4"
        mock_board_state.undo.assert_called_once()

    def test_undo_move_at_start_position(self, mock_board_state):
        """Test that undoing fails safely if the board is at the starting position."""
        mock_board_state.is_start_pos = True
        
        result = MoveHelper.undo_move(mock_board_state)
        
        assert result is None
        mock_board_state.undo.assert_not_called()

    # --- get_san_for_move Tests ---

    def test_get_san_for_move_valid(self, mock_board_state):
        """Test that a valid UCI string is correctly converted to SAN."""
        test_move = chess.Move.from_uci("e2e4")
        mock_board_state.legal_moves = [test_move]
        mock_board_state.san.return_value = "e4"
        
        result = MoveHelper.get_san_for_move(mock_board_state, "e2e4")
        
        assert result == "e4"
        mock_board_state.san.assert_called_once_with(test_move)

    def test_get_san_for_move_invalid(self, mock_board_state):
        """Test that an invalid or illegal move returns the original UCI string as a fallback."""
        mock_board_state.legal_moves = []
        
        # Try a move that isn't in legal_moves
        result = MoveHelper.get_san_for_move(mock_board_state, "e2e4")
        
        assert result == "e2e4"
        mock_board_state.san.assert_not_called()

    # --- format_uci_sequence Tests ---

    def test_format_uci_sequence_valid(self):
        """Test formatting a clean sequence of valid UCI moves."""
        # We use a real chess.Board here because the helper accepts it and relies heavily on python-chess logic
        board = chess.Board()
        uci_moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
        
        result = MoveHelper.format_uci_sequence(board, uci_moves)
        
        assert result == "1. e4 e5 2. Nf3 Nc6"

    def test_format_uci_sequence_black_to_move(self):
        """Test formatting a sequence that starts from black's turn."""
        board = chess.Board()
        board.push_uci("e2e4") # Now it's Black's turn
        uci_moves = ["e7e5", "g1f3"]
        
        result = MoveHelper.format_uci_sequence(board, uci_moves)
        
        assert result == "1... e5 2. Nf3"

    def test_format_uci_sequence_with_invalid_move(self):
        """Test that formatting handles illegal moves gracefully without crashing."""
        board = chess.Board()
        # "e2e5" is an illegal move, "e7e5" is Black's move but White hasn't moved.
        uci_moves = ["e2e4", "invalid", "g1f3"]
        
        result = MoveHelper.format_uci_sequence(board, uci_moves)
        
        # It should format e4 normally, fallback to "invalid g1f3" as raw string
        assert result == "1. e4 invalid g1f3"
        
    def test_format_uci_sequence_empty(self):
        """Test that formatting an empty list returns an empty string."""
        board = chess.Board()
        assert MoveHelper.format_uci_sequence(board, []) == ""