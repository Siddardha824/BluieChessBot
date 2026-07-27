import pytest
from unittest.mock import MagicMock, patch
import chess
from gui.app.game.models.game_state import GameMode, MatchStatus
from gui.app.game.manager.game_manager import GameManager


class TestGameManager:
    """Test suite for the GameManager controller facade."""

    @pytest.fixture
    def mock_components(self):
        """Fixture to patch GameState and GameService inside GameManager."""
        with patch("gui.app.game.manager.game_manager.GameState") as mock_state_class, \
             patch("gui.app.game.manager.game_manager.GameService") as mock_service_class:

            mock_state = MagicMock()
            mock_state_class.return_value = mock_state

            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            yield mock_state, mock_service

    @pytest.fixture
    def manager(self, mock_components):
        """Fixture to provide a GameManager instance with mocked components."""
        return GameManager(parent=None)

    # --- Initialization & Signal Connections Tests ---

    def test_initialization_and_signal_forwarding(self, mock_components, manager):
        """Verify that manager connects underlying service signals to public signals."""
        mock_state, mock_service = mock_components

        # Verify QObject state and service aggregation
        assert manager._state == mock_state
        assert manager._game_service == mock_service

        # Verify signal connections (setup_engine, make_move, etc.)
        mock_service.setup_engine.connect.assert_called_once()
        mock_service.remove_engine.connect.assert_called_once()
        mock_service.set_engine_position.connect.assert_called_once()
        mock_service.start_engine_search.connect.assert_called_once()
        mock_service.stop_engine_search.connect.assert_called_once()
        mock_service.new_game.connect.assert_called_once()
        mock_service.make_move.connect.assert_called_once()

        # Verify status signal connection
        mock_state.match_status_changed.connect.assert_called_once_with(manager._on_match_status_changed)

    # --- Properties Tests ---

    def test_properties_getters_and_setters(self, mock_components, manager):
        """Verify state properties map correctly through manager properties."""
        mock_state, _ = mock_components

        mock_state.mode = GameMode.PLAY_WHITE
        assert manager.mode == mock_state.mode

        manager.mode = GameMode.ANALYSIS
        assert mock_state.mode == GameMode.ANALYSIS

        mock_state.match_status = MatchStatus.CHECKMATE
        assert manager.status == MatchStatus.CHECKMATE

    # --- Delegation Tests ---

    def test_start_game(self, mock_components, manager, qtbot):
        """Verify start_game delegates to service and emits game_started."""
        _, mock_service = mock_components

        with qtbot.waitSignal(manager.game_started, timeout=1000):
            manager.start_game("path/w", "path/b")

        mock_service.start_game.assert_called_once_with("path/w", "path/b")

    def test_stop_game(self, mock_components, manager, qtbot):
        """Verify stop_game aborts active engine searches and emits game_stopped."""
        _, mock_service = mock_components

        with qtbot.waitSignal(manager.game_stopped, timeout=1000):
            manager.stop_game()

        mock_service.abort_game.assert_called_once()

    @pytest.mark.parametrize(
        "mode, w_engine, b_engine, expected",
        [
            (GameMode.ANALYSIS, "Analysis", None, None),
            (GameMode.PLAY_WHITE, "White", "Black", ["White"]),
            (GameMode.PLAY_BLACK, "White", "Black", ["Black"]),
            (GameMode.ENGINE_VS_ENGINE, "White", "Black", ["White", "Black"]),
        ]
    )
    def test_get_active_engines(self, mode, w_engine, b_engine, expected, mock_components, manager):
        """Verify get_active_engines returns correct engine names depending on game mode."""
        mock_state, mock_service = mock_components
        mock_state.mode = mode
        mock_service._white_engine = w_engine
        mock_service._black_engine = b_engine

        assert manager.get_active_engines() == expected

    @patch("gui.app.game.manager.game_manager.GameSaver")
    def test_save_game_success(self, mock_saver, manager, qtbot):
        """Verify save_game delegates to saver and emits game_saved signal on success."""
        mock_saver.save_pgn.return_value = True
        mock_node = MagicMock()
        engine_info = {"name": "Stockfish"}

        with qtbot.waitSignal(manager.game_saved, timeout=1000):
            manager.save_game("test.pgn", mock_node, engine_info)

        mock_saver.save_pgn.assert_called_once_with("test.pgn", mock_node, engine_info)

    @patch("gui.app.game.manager.game_manager.GameSaver")
    def test_save_game_failure(self, mock_saver, manager, qtbot):
        """Verify save_game does not emit signal if saver returns False."""
        mock_saver.save_pgn.return_value = False
        mock_node = MagicMock()

        with qtbot.assertNotEmitted(manager.game_saved):
            manager.save_game("test.pgn", mock_node, {})

    def test_on_view_changed(self, mock_components, manager):
        """Verify on_view_changed delegates to service."""
        _, mock_service = mock_components
        mock_node = MagicMock()

        manager.on_view_changed(mock_node)

        mock_service.on_view_changed.assert_called_once_with(mock_node)

    def test_on_best_move_updated(self, mock_components, manager):
        """Verify on_best_move_updated delegates to service."""
        _, mock_service = mock_components

        manager.on_best_move_updated("engine_name", "e2e4")

        mock_service.on_best_move_updated.assert_called_once_with("engine_name", "e2e4")

    # --- Match Status Signal Bubbling/Translation Tests ---

    @pytest.mark.parametrize(
        "turn, expected_result",
        [
            (chess.BLACK, "1-0"),  # White wins (it was Black's turn to play, but is checkmated)
            (chess.WHITE, "0-1"),  # Black wins (it was White's turn to play, but is checkmated)
        ]
    )
    def test_match_status_checkmate_bubbling(self, turn, expected_result, mock_components, manager, qtbot):
        """Verify checkmate updates emit game_over with the correct chess result code."""
        mock_state, _ = mock_components
        mock_state.current_turn = turn

        with qtbot.waitSignal(manager.game_over, timeout=1000) as blocker:
            manager._on_match_status_changed(MatchStatus.CHECKMATE)

        assert blocker.args == [expected_result, "Checkmate"]

    def test_match_status_draw_bubbling(self, manager, qtbot):
        """Verify draw updates emit game_over with standard draw result code."""
        with qtbot.waitSignal(manager.game_over, timeout=1000) as blocker:
            manager._on_match_status_changed(MatchStatus.DRAW)

        assert blocker.args == ["1/2-1/2", "Draw"]

    def test_match_status_aborted_bubbling(self, manager, qtbot):
        """Verify aborted updates emit game_stopped."""
        with qtbot.waitSignal(manager.game_stopped, timeout=1000):
            manager._on_match_status_changed(MatchStatus.ABORTED)
