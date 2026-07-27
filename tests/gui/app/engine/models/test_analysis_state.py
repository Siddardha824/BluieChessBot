import pytest
from gui.app.engine.models.analysis_state import AnalysisState


class TestAnalysisState:
    """Test suite for the reactive AnalysisState model."""

    @pytest.fixture
    def analysis_state(self):
        """Fixture to provide a fresh, isolated AnalysisState model."""
        return AnalysisState(parent=None)

    # --- Initialization Tests ---

    def test_initialization(self, analysis_state):
        """Verify that the analysis state initializes with default values."""
        assert analysis_state.depth == 0
        assert analysis_state.nps == 0
        assert analysis_state.nodes == 0
        assert analysis_state.time_ms == 0
        assert analysis_state.score == 0.0
        assert analysis_state.is_mate is False
        assert analysis_state.mate_in is None
        assert analysis_state.pv == []
        assert analysis_state.best_move is None

    # --- Property Getters and Setters Tests ---

    def test_property_setters_and_getters(self, analysis_state):
        """Verify that properties can be set and get correctly."""
        analysis_state.depth = 14
        analysis_state.nps = 150000
        analysis_state.nodes = 1200000
        analysis_state.time_ms = 8000
        analysis_state.score = 2.45
        analysis_state.is_mate = True
        analysis_state.mate_in = -4
        analysis_state.pv = ["e2e4", "e7e5", "g1f3"]
        analysis_state.best_move = "e2e4"

        assert analysis_state.depth == 14
        assert analysis_state.nps == 150000
        assert analysis_state.nodes == 1200000
        assert analysis_state.time_ms == 8000
        assert analysis_state.score == 2.45
        assert analysis_state.is_mate is True
        assert analysis_state.mate_in == -4
        assert analysis_state.pv == ["e2e4", "e7e5", "g1f3"]
        assert analysis_state.best_move == "e2e4"

    # --- Signal and Notification Tests ---

    def test_setters_do_not_emit_signals(self, analysis_state, qtbot):
        """Verify that modifying individual properties does not trigger signals to prevent signal storms."""
        with qtbot.assertNotEmitted(analysis_state.analysis_state_changed):
            analysis_state.depth = 5
            analysis_state.score = 1.0
            analysis_state.best_move = "d2d4"

    def test_notify_updated_emits_signal(self, analysis_state, qtbot):
        """Verify that notify_updated explicitly emits analysis_state_changed."""
        with qtbot.waitSignal(analysis_state.analysis_state_changed, timeout=1000):
            analysis_state.notify_updated()

    # --- Reset State Tests ---

    def test_reset_clears_telemetry_and_emits_signal(self, analysis_state, qtbot):
        """Verify that reset restores all properties to default and emits analysis_state_changed."""
        # Arrange - set some custom values
        analysis_state.depth = 10
        analysis_state.score = -1.5
        analysis_state.pv = ["d2d4"]
        analysis_state.best_move = "d2d4"

        # Act & Assert signal emission
        with qtbot.waitSignal(analysis_state.analysis_state_changed, timeout=1000):
            analysis_state.reset()

        # Assert property restoration
        assert analysis_state.depth == 0
        assert analysis_state.nps == 0
        assert analysis_state.nodes == 0
        assert analysis_state.time_ms == 0
        assert analysis_state.score == 0.0
        assert analysis_state.is_mate is False
        assert analysis_state.mate_in is None
        assert analysis_state.pv == []
        assert analysis_state.best_move is None
