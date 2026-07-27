import json
import pytest
from unittest.mock import MagicMock
from gui.app.game.services.game_saver import GameSaver


class TestGameSaver:
    """Test suite for the GameSaver PGN export service."""

    @pytest.fixture
    def mock_node(self):
        """Fixture to provide a mock MoveNode."""
        node = MagicMock()
        node.headers = {}
        return node

    def test_save_pgn_success(self, mock_node, tmp_path):
        """Verify that save_pgn writes PGN content, includes engine headers, and returns True."""
        filepath = tmp_path / "game.pgn"
        engine_info = {"threads": 4, "hash": 128}

        success = GameSaver.save_pgn(str(filepath), mock_node, engine_info)

        assert success is True
        assert filepath.exists()
        assert mock_node.headers["Engine"] == json.dumps(engine_info)
        mock_node.accept.assert_called_once()

    def test_save_pgn_failure_io_exception(self, mock_node, tmp_path):
        """Verify that save_pgn returns False safely if write operation fails."""
        # Point to a directory to force an IO exception
        filepath = tmp_path

        success = GameSaver.save_pgn(str(filepath), mock_node, engine_info={})
        assert success is False
