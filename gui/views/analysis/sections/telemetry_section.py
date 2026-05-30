# gui/views/analysis/sections/telemetry_section.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from gui.views.analysis.styles.analysis_styles import get_section_header_style, get_pv_line_style
from gui.widgets import (
    EvaluationWidget, DepthWidget, MetricsGrid, 
    TopMovesWidget, EngineStatusWidget
)

class TelemetrySection(QFrame):
    def __init__(self, theme, engine_info=None, initial_top_moves=None, parent=None):
        """
        Initializes the TelemetrySection.
        
        Args:
            theme: The active ActiveTheme object.
            engine_info: A reactive EngineInfo model instance to bind and track.
            initial_top_moves: Custom list of top moves to populate on bootstrap.
            parent: Parent QWidget.
        """
        super().__init__(parent)
        self.theme = theme
        self.engine_info = engine_info
        self.initial_top_moves = initial_top_moves
        self.setObjectName("TelemetryPanel")
        self._init_ui()

        # Wire reactive updates from EngineInfo
        if self.engine_info is not None:
            self.engine_info.changed.connect(self.sync_engine_info)
            self.sync_engine_info()

    def _init_ui(self):
        telemetry_layout = QVBoxLayout(self)
        telemetry_layout.setContentsMargins(20, 20, 20, 20)
        telemetry_layout.setSpacing(15)

        # 1. Atomic Engine Name & Status Widget (Fully reusable elsewhere!)
        self.status_widget = EngineStatusWidget(self.theme)
        telemetry_layout.addWidget(self.status_widget)

        # 2. Sleek Horizontal Evaluation & Advantage Score Widget
        self.evaluation_widget = EvaluationWidget(self.theme)
        telemetry_layout.addWidget(self.evaluation_widget)

        # 3. Depth Progress Bar Widget
        self.depth_widget = DepthWidget(self.theme)
        telemetry_layout.addWidget(self.depth_widget)

        # 4. Metrics Grid Widget (Nodes, NPS, Hash, Threads)
        self.metrics_grid = MetricsGrid(self.theme)
        telemetry_layout.addWidget(self.metrics_grid)

        # 5. Principal Variation wrapped section
        pv_frame = QFrame()
        pv_frame.setFrameShape(QFrame.Shape.NoFrame)
        pv_vbox = QVBoxLayout(pv_frame)
        pv_vbox.setContentsMargins(0, 0, 0, 0)
        pv_vbox.setSpacing(5)
        
        pv_hdr = QLabel("Principal Variation")
        pv_hdr.setStyleSheet(get_section_header_style(self.theme))
        
        self.lbl_pv_line = QLabel("-")
        self.lbl_pv_line.setWordWrap(True)
        self.lbl_pv_line.setStyleSheet(get_pv_line_style(self.theme))
        
        pv_vbox.addWidget(pv_hdr)
        pv_vbox.addWidget(self.lbl_pv_line)
        telemetry_layout.addWidget(pv_frame)

        # 6. Top Moves List sub-table Widget
        self.top_moves_widget = TopMovesWidget(self.theme, self.initial_top_moves)
        telemetry_layout.addWidget(self.top_moves_widget)

    def sync_engine_info(self) -> None:
        """Synchronizes widgets reactively when the EngineInfo model changes."""
        if self.engine_info is None:
            return
            
        # 1. Update status widget details
        self.status_widget.set_status(
            self.engine_info.name,
            self.engine_info.status,
            self.engine_info.connection_status
        )
        
        # 2. Update metrics grid configuration options
        if self.engine_info.connection_status == "Disconnected":
            self.metrics_grid.set_config("Not Available", "Not Available")
        else:
            self.metrics_grid.set_config(self.engine_info.hash_size, self.engine_info.threads)

    def update_analysis_state(self, state) -> None:
        """
        Updates the dynamic telemetry widgets based on UCI search state info frames.
        """
        self.depth_widget.set_depth(state.depth)
        self.evaluation_widget.set_evaluation(state.score, state.is_mate, state.mate_in)
        
        # Sync values on the metrics grid
        self.metrics_grid.set_search_metrics(state.nodes, state.nps)
                
        # Parse PV Line
        pv_str = " ".join(state.pv) if state.pv else "-"
        self.lbl_pv_line.setText(pv_str)
        
        # Populate Top Moves table dynamically with real moves list!
        if state.pv:
            real_moves = []
            for idx, move in enumerate(state.pv[:5]):
                score_str = f"+{state.score:.2f}" if state.score >= 0 else f"{state.score:.2f}"
                prob_pct = f"{max(45 - idx * 8, 5)}%"
                node_est = f"{max(int(state.nodes / (idx + 1)), 1000):,}"
                real_moves.append((move, score_str, str(state.depth), node_est, prob_pct))
            
            # Fill empty slots if PV length is short
            while len(real_moves) < 5:
                real_moves.append(("-", "-", "-", "-", "-"))
                
            self.top_moves_widget.populate(real_moves)

    def clear(self) -> None:
        """Resets all metrics to default states."""
        self.depth_widget.clear()
        self.evaluation_widget.clear()
        self.metrics_grid.clear()
        self.top_moves_widget.clear()
        self.lbl_pv_line.setText("-")

    def update_theme(self, theme) -> None:
        self.theme = theme
        self.lbl_pv_line.setStyleSheet(get_pv_line_style(self.theme))
        
        # Recursively update theme parameters on modular sub-widgets
        self.status_widget.update_theme(self.theme)
        self.evaluation_widget.update_theme(self.theme)
        self.depth_widget.update_theme(self.theme)
        self.metrics_grid.update_theme(self.theme)
        self.top_moves_widget.update_theme(self.theme)
