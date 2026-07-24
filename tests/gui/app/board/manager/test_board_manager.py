import pytest
import chess
from unittest.mock import patch

from gui.app.board.manager.board_manager import BoardManager
from gui.app.board.services.move_node import MoveNode


class TestBoardManager:
    """Test suite for the BoardManager controller."""

    @pytest.fixture
    def board_manager(self, qtbot):
        """Fixture to provide a fresh BoardManager instance."""
        manager = BoardManager(parent=None)
        return manager

    # --- Signal Propagation Tests ---

    def test_signal_propagation(self, board_manager, qtbot):
        """Verify that view_changed signals from the internal BoardState bubble up to the BoardManager."""
        mock_node = MoveNode()
        
        # We listen to the MANAGER'S signal
        with qtbot.waitSignal(board_manager.view_changed, timeout=1000) as blocker:
            # We artificially trigger the internal STATE'S signal
            board_manager._state.view_changed.emit(mock_node)
            
        # Ensure the payload was passed through cleanly
        assert blocker.args[0] == mock_node

    # --- MoveHelper Delegation Tests ---

    @patch("gui.app.board.manager.board_manager.MoveHelper")
    def test_make_move(self, mock_move_helper, board_manager):
        """Verify make_move delegates correctly and returns the success boolean."""
        # Test a successful move
        mock_move_helper.make_move.return_value = True
        assert board_manager.make_move("e2e4") is True
        mock_move_helper.make_move.assert_called_with(board_manager._state, "e2e4")
        
        # Test a rejected move
        mock_move_helper.make_move.return_value = False
        assert board_manager.make_move("invalid") is False

    @patch("gui.app.board.manager.board_manager.MoveHelper")
    def test_undo_move(self, mock_move_helper, board_manager):
        """Verify undo_move delegates to MoveHelper and returns the undone UCI string."""
        mock_move_helper.undo_move.return_value = "e2e4"
        
        assert board_manager.undo_move() == "e2e4"
        mock_move_helper.undo_move.assert_called_once_with(board_manager._state)

    @patch("gui.app.board.manager.board_manager.MoveHelper")
    def test_get_san_for_move(self, mock_move_helper, board_manager):
        """Verify SAN formatting is correctly requested from the helper."""
        mock_move_helper.get_san_for_move.return_value = "e4"
        
        assert board_manager.get_san_for_move("e2e4") == "e4"
        mock_move_helper.get_san_for_move.assert_called_once_with(board_manager._state, "e2e4")

    @patch("gui.app.board.manager.board_manager.MoveHelper")
    def test_format_uci_sequence(self, mock_move_helper, board_manager):
        """Verify sequence formatting is correctly requested from the helper."""
        mock_move_helper.format_uci_sequence.return_value = "1. e4 e5"
        
        assert board_manager.format_uci_sequence(["e2e4", "e7e5"]) == "1. e4 e5"
        mock_move_helper.format_uci_sequence.assert_called_once_with(board_manager._state, ["e2e4", "e7e5"])

    # --- BoardState Delegation Tests ---

    def test_new_game(self, board_manager):
        """Verify that starting a new game calls reset on the internal state."""
        with patch.object(board_manager._state, 'reset') as mock_reset:
            board_manager.new_game()
            mock_reset.assert_called_once()

    def test_load_fen_valid(self, board_manager):
        """Verify that valid FEN strings are loaded into the state."""
        with patch.object(board_manager._state, 'is_valid_fen', return_value=True), \
             patch.object(board_manager._state, 'set_fen') as mock_set_fen:
            
            board_manager.load_fen("valid_fen_string")
            mock_set_fen.assert_called_once_with("valid_fen_string")

    def test_load_fen_invalid(self, board_manager):
        """Verify that invalid FEN strings are rejected and not passed to set_fen."""
        with patch.object(board_manager._state, 'is_valid_fen', return_value=False), \
             patch.object(board_manager._state, 'set_fen') as mock_set_fen:
            
            board_manager.load_fen("invalid_fen_string")
            mock_set_fen.assert_not_called()

    def test_get_fen(self, board_manager):
        """Verify get_fen reads directly from the state's property."""
        # Using the actual BoardState integration here to verify it reads correctly
        assert board_manager.get_fen() == chess.STARTING_FEN

    def test_get_export_state(self, board_manager):
        """Verify that the manager correctly exposes the root MoveNode tree."""
        node = board_manager.get_export_state()
        
        assert isinstance(node, MoveNode)
        assert node == board_manager._state.game_tree