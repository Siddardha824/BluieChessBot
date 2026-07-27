import pytest
import chess
from gui.app.game.models.game_state import GameState, GameMode, MatchStatus


class TestGameState:
    """Test suite for the reactive GameState model."""

    @pytest.fixture
    def state(self):
        """Fixture to provide a fresh GameState instance."""
        return GameState(parent=None)

    # --- Initialization Tests ---

    def test_initialization(self, state):
        """Verify that game state initializes with default values."""
        assert state.mode == GameMode.ANALYSIS
        assert state.match_status == MatchStatus.ACTIVE
        assert state.current_turn == chess.WHITE
        assert state._white_time == 0.0
        assert state._black_time == 0.0

    # --- Property Setters & Signal Emitted Tests ---

    def test_mode_change_emits_signal(self, state, qtbot):
        """Verify that modifying game mode updates state and emits the game_mode_changed signal."""
        with qtbot.waitSignal(state.game_mode_changed, timeout=1000) as blocker:
            state.mode = GameMode.PLAY_BLACK

        assert state.mode == GameMode.PLAY_BLACK
        assert blocker.args[0] == GameMode.PLAY_BLACK

        # Test setting duplicate does not emit
        with qtbot.assertNotEmitted(state.game_mode_changed):
            state.mode = GameMode.PLAY_BLACK

    def test_match_status_change_emits_signal(self, state, qtbot):
        """Verify that modifying match status updates state and emits match_status_changed."""
        with qtbot.waitSignal(state.match_status_changed, timeout=1000) as blocker:
            state.match_status = MatchStatus.CHECKMATE

        assert state.match_status == MatchStatus.CHECKMATE
        assert blocker.args[0] == MatchStatus.CHECKMATE

        # Test duplicate settings do not emit
        with qtbot.assertNotEmitted(state.match_status_changed):
            state.match_status = MatchStatus.CHECKMATE

    def test_current_turn_change_emits_signal(self, state, qtbot):
        """Verify that modifying current turn updates state and emits turn_changed."""
        with qtbot.waitSignal(state.turn_changed, timeout=1000) as blocker:
            state.current_turn = chess.BLACK

        assert state.current_turn == chess.BLACK
        assert blocker.args[0] == chess.BLACK

        # Test duplicate turn settings do not emit
        with qtbot.assertNotEmitted(state.turn_changed):
            state.current_turn = chess.BLACK

    # --- Clock and Reset Tests ---

    def test_update_clocks(self, state, qtbot):
        """Verify that update_clocks sets the times and emits clocks_updated signal."""
        with qtbot.waitSignal(state.clocks_updated, timeout=1000) as blocker:
            state.update_clocks(120.5, 95.2)

        assert state._white_time == 120.5
        assert state._black_time == 95.2
        assert blocker.args[0] == 120.5
        assert blocker.args[1] == 95.2

    def test_reset(self, state, qtbot):
        """Verify that reset restores all match stats to default and emits relevant signals."""
        state.match_status = MatchStatus.CHECKMATE
        state.current_turn = chess.BLACK
        state.update_clocks(60.0, 30.0)

        # Act & Assert signal emissions
        with qtbot.waitSignal(state.match_status_changed, timeout=1000) as blocker_status, \
             qtbot.waitSignal(state.turn_changed, timeout=1000) as blocker_turn, \
             qtbot.waitSignal(state.clocks_updated, timeout=1000) as blocker_clocks:
            state.reset()

        assert state.match_status == MatchStatus.ACTIVE
        assert state.current_turn == chess.WHITE
        assert state._white_time == 0.0
        assert state._black_time == 0.0

        assert blocker_status.args[0] == MatchStatus.ACTIVE
        assert blocker_turn.args[0] == chess.WHITE
        assert blocker_clocks.args[0] == 0.0
        assert blocker_clocks.args[1] == 0.0
