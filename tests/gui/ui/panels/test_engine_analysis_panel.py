"""
Unit tests for the EngineAnalysisPanel UI component.

This module verifies that the EngineAnalysisPanel correctly initializes,
updates its evaluation score, depth, NPS, nodes, and principal variation (PV)
move strings, and clamps progress bar values as appropriate.
"""

from gui.ui.panels.engine_analysis_panel import EngineAnalysisPanel


class AnalysisStateDummy:
    """Mock/Dummy class representing the engine analysis state payload.

    This class mimics the attributes expected by the EngineAnalysisPanel's
    update_analysis slot, including evaluation scores, mate status, search depth,
    node and nps metrics, and principal variation (PV) moves.
    """

    def __init__(
        self,
        depth: int = 0,
        score: int = 0,
        is_mate: bool = False,
        mate_in: int = 0,
        nps: int = 0,
        nodes: int = 0,
        best_move: str | None = None,
        pv: list[str] | None = None,
    ):
        """Initialize the dummy analysis state.

        Args:
            depth: The search depth in plies.
            score: The evaluation score in centipawns.
            is_mate: True if a forced mate is detected.
            mate_in: The number of moves to mate.
            nps: Nodes searched per second.
            nodes: Total number of nodes searched.
            best_move: The best move found.
            pv: The list of moves in the principal variation.
        """
        self.depth = depth
        self.score = score
        self.is_mate = is_mate
        self.mate_in = mate_in
        self.nps = nps
        self.nodes = nodes
        self.best_move = best_move
        self.pv = pv or []


class TestEngineAnalysisPanel:
    """Test suite for the isolated EngineAnalysisPanel UI component.

    This suite verifies that initialization via _setup_ui correctly constructs the
    telemetry labels, progress bar, and PV text area, and that state updates
    for centipawn scores, mate scores, clamping, and PV text formatting function
    as expected.
    """

    def test_initialization_and_theming_hooks(self, qtbot):
        """Verify that the widget initializes with default text, ranges, and QSS object names."""
        # Arrange & Act
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)

        # Assert
        assert panel.objectName() == "engineAnalysisPanel"
        assert panel.eval_bar.objectName() == "evalBar"
        assert panel.score_label.objectName() == "scoreLabel"
        assert panel.depth_label.objectName() == "depthLabel"
        assert panel.nps_label.objectName() == "npsLabel"
        assert panel.nodes_label.objectName() == "nodesLabel"
        assert panel.pv_text.objectName() == "pvTextEdit"

        assert panel.score_label.text() == "Score: 0.00"
        assert panel.depth_label.text() == "Depth: 0/0"
        assert panel.nps_label.text() == "NPS: 0"
        assert panel.nodes_label.text() == "Nodes: 0"
        assert panel.pv_text.toPlainText() == ""

        assert panel.eval_bar.minimum() == -1000
        assert panel.eval_bar.maximum() == 1000
        assert panel.eval_bar.value() == 0
        assert not panel.eval_bar.isTextVisible()
        assert panel.pv_text.isReadOnly()
        assert panel.pv_text.placeholderText() == "Waiting for engine analysis..."

    def test_update_analysis_score(self, qtbot):
        """Verify that update_analysis correctly displays standard centipawn scores, telemetry metrics, and PV moves."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state = AnalysisStateDummy(
            depth=12,
            score=150,
            is_mate=False,
            nps=100000,
            nodes=500000,
            best_move="e2e4",
            pv=["e2e4", "e7e5"],
        )

        # Act
        panel.update_analysis(state)

        # Assert
        assert panel.score_label.text() == "Score: +1.50"
        assert panel.eval_bar.value() == 150
        assert panel.depth_label.text() == "Depth: 12/12"
        assert panel.nps_label.text() == "NPS: 100000"
        assert panel.nodes_label.text() == "Nodes: 500000"
        assert panel.pv_text.toPlainText() == "Best Move: e2e4\ne2e4 e7e5"

    def test_update_analysis_mate_positive(self, qtbot):
        """Verify that update_analysis correctly displays positive forced mate scores."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state = AnalysisStateDummy(
            depth=8,
            is_mate=True,
            mate_in=3,
            nps=12000,
            nodes=96000,
            best_move="f7f8q",
            pv=["f7f8q", "g7g6"],
        )

        # Act
        panel.update_analysis(state)

        # Assert
        assert panel.score_label.text() == "Score: M3"
        assert panel.eval_bar.value() == 1000
        assert panel.depth_label.text() == "Depth: 8/8"
        assert panel.nps_label.text() == "NPS: 12000"
        assert panel.nodes_label.text() == "Nodes: 96000"
        assert panel.pv_text.toPlainText() == "Best Move: f7f8q\nf7f8q g7g6"

    def test_update_analysis_mate_negative(self, qtbot):
        """Verify that update_analysis correctly displays negative forced mate scores."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state = AnalysisStateDummy(
            depth=7,
            is_mate=True,
            mate_in=-5,
            nps=8000,
            nodes=56000,
            best_move="e1g1",
            pv=["e1g1"],
        )

        # Act
        panel.update_analysis(state)

        # Assert
        assert panel.score_label.text() == "Score: M-5"
        assert panel.eval_bar.value() == -1000
        assert panel.depth_label.text() == "Depth: 7/7"
        assert panel.nps_label.text() == "NPS: 8000"
        assert panel.nodes_label.text() == "Nodes: 56000"
        assert panel.pv_text.toPlainText() == "Best Move: e1g1\ne1g1"

    def test_update_analysis_clamp_max_score(self, qtbot):
        """Verify that update_analysis clamps the progress bar value to +1000 for extremely high scores."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state = AnalysisStateDummy(score=1500)

        # Act
        panel.update_analysis(state)

        # Assert
        assert panel.score_label.text() == "Score: +15.00"
        assert panel.eval_bar.value() == 1000

    def test_update_analysis_clamp_min_score(self, qtbot):
        """Verify that update_analysis clamps the progress bar value to -1000 for extremely low scores."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state = AnalysisStateDummy(score=-1200)

        # Act
        panel.update_analysis(state)

        # Assert
        assert panel.score_label.text() == "Score: -12.00"
        assert panel.eval_bar.value() == -1000

    def test_update_analysis_empty_pv_and_best_move(self, qtbot):
        """Verify that update_analysis clears the PV text area when both best move and PV are empty."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state_with_pv = AnalysisStateDummy(best_move="e2e4", pv=["e2e4", "e7e5"])
        state_empty = AnalysisStateDummy(best_move=None, pv=None)

        # Act & Assert
        panel.update_analysis(state_with_pv)
        assert panel.pv_text.toPlainText() == "Best Move: e2e4\ne2e4 e7e5"

        panel.update_analysis(state_empty)
        assert panel.pv_text.toPlainText() == ""

    def test_update_analysis_best_move_only(self, qtbot):
        """Verify that update_analysis correctly formats text when only best move is present."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state = AnalysisStateDummy(best_move="e2e4", pv=None)

        # Act
        panel.update_analysis(state)

        # Assert
        assert panel.pv_text.toPlainText() == "Best Move: e2e4\n"

    def test_update_analysis_pv_only(self, qtbot):
        """Verify that update_analysis correctly formats text when only PV moves are present."""
        # Arrange
        panel = EngineAnalysisPanel(parent=None)
        qtbot.addWidget(panel)
        state = AnalysisStateDummy(best_move=None, pv=["e2e4", "e7e5"])

        # Act
        panel.update_analysis(state)

        # Assert
        assert panel.pv_text.toPlainText() == "e2e4 e7e5"
