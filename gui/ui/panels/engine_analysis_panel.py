"""
Engine analysis panel component for displaying real-time chess engine search metrics.

This module provides the EngineAnalysisPanel widget, which visualizes engine evaluation,
depth, selective depth, and principal variation (PV) move suggestions.
"""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QLabel, QProgressBar, QTextEdit
from gui.ui.core.styled_widget import StyledWidget


class EngineAnalysisPanel(StyledWidget):
    """
    Panel widget displaying evaluation score, search depth, and principal variation.

    This component serves as a View Widget in the MVVM architecture, listening to
    engine search analysis states and displaying them via a score bar, labels,
    and a move list text editor.

    Styling:
        Relies on the `#engineAnalysisPanel` object name for QSS styling.
        The score bar is named `#evalBar`.
        The score label is named `#scoreLabel`.
        The depth label is named `#depthLabel`.
        The NPS label is named `#npsLabel`.
        The nodes label is named `#nodesLabel`.
        The PV text area is named `#pvTextEdit`.
    """

    # --- UI Initialization ---

    def __init__(self, parent):
        """Initialize the engine analysis panel.

        Args:
            parent: The parent QWidget.
        """
        super().__init__(object_name="engineAnalysisPanel", parent=parent)

    # --- Layout Setup ---

    def _setup_ui(self):
        """Set up the layout, evaluation bar, telemetry labels, and text editor."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(8)

        self.eval_bar = QProgressBar()
        self.eval_bar.setObjectName("evalBar")
        self.eval_bar.setRange(-1000, 1000)
        # Hide the progress text on the evaluation bar to use a separate label instead
        self.eval_bar.setTextVisible(False)
        self.eval_bar.setValue(0)
        self._layout.addWidget(self.eval_bar)

        telemetry_layout = QGridLayout()

        self.score_label = QLabel("Score: 0.00")
        self.score_label.setObjectName("scoreLabel")

        self.depth_label = QLabel("Depth: 0/0")
        self.depth_label.setObjectName("depthLabel")

        self.nps_label = QLabel("NPS: 0")
        self.nps_label.setObjectName("npsLabel")

        self.nodes_label = QLabel("Nodes: 0")
        self.nodes_label.setObjectName("nodesLabel")

        telemetry_layout.addWidget(self.score_label, 0, 0)
        telemetry_layout.addWidget(self.depth_label, 0, 1)
        telemetry_layout.addWidget(self.nps_label, 1, 0)
        telemetry_layout.addWidget(self.nodes_label, 1, 1)

        self._layout.addLayout(telemetry_layout)

        self.pv_text = QTextEdit()
        self.pv_text.setObjectName("pvTextEdit")
        self.pv_text.setReadOnly(True)
        self.pv_text.setPlaceholderText("Waiting for engine analysis...")
        self._layout.addWidget(self.pv_text)

    # --- Public Slots (State Updates) ---

    @Slot(object)
    def update_analysis(self, analysis_state):
        """Update the panel widgets with the latest engine analysis state.

        Args:
            analysis_state: The data object containing is_mate, mate_in, score, depth,
                nps, nodes, best_move, and pv.
        """
        if analysis_state.is_mate:
            score_text = f"M{analysis_state.mate_in}"
            # Force max/min progress bar value for mate evaluation
            bar_value = 1000 if analysis_state.mate_in > 0 else -1000
        else:
            # Convert centipawns to standard decimal evaluation
            score_text = f"{analysis_state.score / 100.0:+.2f}"
            # Clamp the bar value so it doesn't exceed the visual range
            bar_value = max(-1000, min(1000, analysis_state.score))

        self.score_label.setText(f"Score: {score_text}")
        self.eval_bar.setValue(bar_value)

        # Display depth values in depth/seldepth format (currently using depth for both)
        self.depth_label.setText(f"Depth: {analysis_state.depth}/{analysis_state.depth}")
        self.nps_label.setText(f"NPS: {analysis_state.nps}")
        self.nodes_label.setText(f"Nodes: {analysis_state.nodes}")

        best_move_string = ""

        # Prepend the best move if it is available in the current analysis state
        if analysis_state.best_move:
            best_move_string = f"Best Move: {analysis_state.best_move}\n"

        pv_string = ""

        # Format the list of moves in the principal variation as a single string
        if analysis_state.pv:
            pv_string = " ".join(analysis_state.pv)

        self.pv_text.setText(best_move_string + pv_string)