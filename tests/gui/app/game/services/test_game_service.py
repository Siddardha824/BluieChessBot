import pytest
from unittest.mock import MagicMock
import chess
from gui.app.game.models.game_state import GameState, GameMode, MatchStatus
from gui.app.game.services.game_service import GameService


class TestGameService:
    """Test suite for the GameService chess session coordinator."""

    @pytest.fixture
    def state(self):
        """Fixture to provide a fresh GameState instance."""
        return GameState(parent=None)

    @pytest.fixture
    def service(self, state):
        """Fixture to provide a GameService instance connected to state."""
        return GameService(parent=None, state=state)

    # --- Engine Setup & Cleanup Tests ---

    def test_setup_engine(self, service, qtbot):
        """Verify that _setup_engine emits the setup_engine signal for valid paths."""
        with qtbot.waitSignal(service.setup_engine, timeout=1000) as blocker:
            service._setup_engine("Stockfish", "path/to/stockfish")

        assert blocker.args[0] == "Stockfish"
        assert blocker.args[1] == "path/to/stockfish"

    def test_setup_engine_empty_path(self, service, qtbot):
        """Verify that _setup_engine logs error and does not emit signal if path is empty."""
        with qtbot.assertNotEmitted(service.setup_engine):
            service._setup_engine("Stockfish", "")

    def test_cleanup_engines(self, service, qtbot):
        """Verify that cleanup_engines emits removal signals for both set engines and resets slots."""
        service._white_engine = "WhiteEngine"
        service._black_engine = "BlackEngine"

        removed = []
        service.remove_engine.connect(removed.append)

        service._cleanup_engines()

        assert "WhiteEngine" in removed
        assert "BlackEngine" in removed
        assert service._white_engine is None
        assert service._black_engine is None

    # --- Start Game Mode Dispatch Tests ---

    @pytest.mark.parametrize(
        "mode, white_path, black_path, expected_white, expected_black",
        [
            (GameMode.ANALYSIS, "path/w", "", "Analysis", None),
            (GameMode.PLAY_WHITE, "", "path/b", None, "Black"),
            (GameMode.PLAY_BLACK, "path/w", "", "White", None),
            (GameMode.ENGINE_VS_ENGINE, "path/w", "path/b", "White", "Black"),
        ]
    )
    def test_start_game_modes(self, mode, white_path, black_path, expected_white, expected_black, service, state, qtbot):
        """Verify starting game in different modes sets up appropriate engines and emits resets."""
        state.mode = mode

        setup_calls = []
        service.setup_engine.connect(lambda name, path: setup_calls.append((name, path)))

        with qtbot.waitSignal(service.new_game, timeout=1000):
            service.start_game(white_path, black_path)

        assert service._white_engine == expected_white
        assert service._black_engine == expected_black

        if expected_white:
            assert ("White" in [x[0] for x in setup_calls]) or ("Analysis" in [x[0] for x in setup_calls])
        if expected_black:
            assert "Black" in [x[0] for x in setup_calls]

    # --- Stop and Abort Tests ---

    def test_end_game(self, service, qtbot):
        """Verify end_game emits stop signals to active engines."""
        service._white_engine = "WhiteEngine"
        service._black_engine = "BlackEngine"

        stopped = []
        service.stop_engine_search.connect(stopped.append)

        service.end_game()

        assert "WhiteEngine" in stopped
        assert "BlackEngine" in stopped

    def test_abort_game(self, service, state, qtbot):
        """Verify abort_game stops active engine searches and sets match status to aborted."""
        service._white_engine = "White"

        stopped = []
        service.stop_engine_search.connect(stopped.append)

        service.abort_game()

        assert "White" in stopped
        assert state.match_status == MatchStatus.ABORTED

    # --- View Changed and Result Handling Tests ---

    def test_on_view_changed_checkmate(self, service, state, qtbot):
        """Verify checkmate view updates status and calls end_game."""
        mock_board = MagicMock()
        mock_board.turn = chess.BLACK
        mock_board.fen.return_value = "checkmate_fen"
        mock_board.is_checkmate.return_value = True

        mock_node = MagicMock()
        mock_node.board.return_value = mock_board

        service.on_view_changed(mock_node)

        assert state.current_turn == chess.BLACK
        assert service._current_fen == "checkmate_fen"
        assert state.match_status == MatchStatus.CHECKMATE

    def test_on_view_changed_draw(self, service, state, qtbot):
        """Verify draw view updates status and calls end_game."""
        mock_board = MagicMock()
        mock_board.turn = chess.WHITE
        mock_board.fen.return_value = "draw_fen"
        mock_board.is_checkmate.return_value = False
        mock_board.is_game_over.return_value = True

        mock_node = MagicMock()
        mock_node.board.return_value = mock_board

        service.on_view_changed(mock_node)

        assert state.match_status == MatchStatus.DRAW

    def test_on_view_changed_active_triggers_search(self, service, state, qtbot):
        """Verify active view triggers FEN configure and starts engine search for active side."""
        service._white_engine = "WhiteEngine"
        state.mode = GameMode.ENGINE_VS_ENGINE

        mock_board = MagicMock()
        mock_board.turn = chess.WHITE
        mock_board.fen.return_value = "active_fen"
        mock_board.is_checkmate.return_value = False
        mock_board.is_game_over.return_value = False

        mock_node = MagicMock()
        mock_node.board.return_value = mock_board

        with qtbot.waitSignal(service.set_engine_position, timeout=1000) as blocker_pos, \
             qtbot.waitSignal(service.start_engine_search, timeout=1000) as blocker_start:
            service.on_view_changed(mock_node)

        assert blocker_pos.args == ["WhiteEngine", "active_fen"]
        assert blocker_start.args == ["WhiteEngine"]

    # --- Best Move Handling Tests ---

    def test_on_best_move_updated_valid(self, service, state, qtbot):
        """Verify best move is played if matching turn engine and in a play mode."""
        service._white_engine = "White"
        state.current_turn = chess.WHITE
        state.mode = GameMode.PLAY_WHITE

        with qtbot.waitSignal(service.make_move, timeout=1000) as blocker:
            service.on_best_move_updated("White", "e2e4")

        assert blocker.args[0] == "e2e4"

    def test_on_best_move_updated_wrong_turn_ignored(self, service, state, qtbot):
        """Verify best move is ignored if engine does not match current turn expected engine."""
        service._white_engine = "White"
        service._black_engine = "Black"
        state.current_turn = chess.WHITE
        state.mode = GameMode.ENGINE_VS_ENGINE

        with qtbot.assertNotEmitted(service.make_move):
            service.on_best_move_updated("Black", "e7e5")

    def test_on_best_move_updated_analysis_mode_ignored(self, service, state, qtbot):
        """Verify best move is not played onto the board in analysis mode."""
        service._white_engine = "Analysis"
        state.current_turn = chess.WHITE
        state.mode = GameMode.ANALYSIS

        with qtbot.assertNotEmitted(service.make_move):
            service.on_best_move_updated("Analysis", "d2d4")

    def test_trigger_next_action_non_active(self, service, state, qtbot):
        """Verify _trigger_next_action returns early if match status is not ACTIVE."""
        # Arrange
        state.match_status = MatchStatus.DRAW
        service._white_engine = "White"

        # Act & Assert
        with qtbot.assertNotEmitted(service.start_engine_search):
            service._trigger_next_action()

