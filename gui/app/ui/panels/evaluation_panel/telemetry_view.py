from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QTextEdit, QStackedWidget
)

class TelemetryView(QWidget):
    """
    Handles telemetry display and switching between Single Engine and Dual Engine stats.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("telemetryViewStacked")
        self.stacked = QStackedWidget(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked)
        
        # ---- PAGE 0: Single Engine View ----
        self.page_single = QWidget(self)
        layout_single = QVBoxLayout(self.page_single)
        layout_single.setContentsMargins(0, 0, 0, 0)
        layout_single.setSpacing(6)

        # Telemetry Grid
        grid_single = QGridLayout()
        grid_single.setSpacing(4)
        
        lbl_depth_title = QLabel("Depth:", self)
        lbl_depth_title.setStyleSheet("font-weight: bold;")
        self.lbl_depth = QLabel("0", self)
        self.lbl_depth.setObjectName("telemetryVal")

        lbl_nodes_title = QLabel("Nodes:", self)
        lbl_nodes_title.setStyleSheet("font-weight: bold;")
        self.lbl_nodes = QLabel("0", self)
        self.lbl_nodes.setObjectName("telemetryVal")

        lbl_nps_title = QLabel("NPS:", self)
        lbl_nps_title.setStyleSheet("font-weight: bold;")
        self.lbl_nps = QLabel("0", self)
        self.lbl_nps.setObjectName("telemetryVal")

        lbl_time_title = QLabel("Time:", self)
        lbl_time_title.setStyleSheet("font-weight: bold;")
        self.lbl_time = QLabel("0ms", self)
        self.lbl_time.setObjectName("telemetryVal")

        grid_single.addWidget(lbl_depth_title, 0, 0)
        grid_single.addWidget(self.lbl_depth, 0, 1)
        grid_single.addWidget(lbl_time_title, 0, 2)
        grid_single.addWidget(self.lbl_time, 0, 3)
        grid_single.addWidget(lbl_nodes_title, 1, 0)
        grid_single.addWidget(self.lbl_nodes, 1, 1)
        grid_single.addWidget(lbl_nps_title, 1, 2)
        grid_single.addWidget(self.lbl_nps, 1, 3)
        layout_single.addLayout(grid_single)

        # PV Line Section
        lbl_pv_title = QLabel("Best Line (PV):", self)
        lbl_pv_title.setStyleSheet("font-weight: bold;")
        self.txt_pv = QTextEdit(self)
        self.txt_pv.setObjectName("pvTextArea")
        self.txt_pv.setReadOnly(True)
        self.txt_pv.setMinimumHeight(45)
        self.txt_pv.setMaximumHeight(80)
        
        layout_single.addWidget(lbl_pv_title)
        layout_single.addWidget(self.txt_pv, 1)

        self.stacked.addWidget(self.page_single)

        # ---- PAGE 1: Dual Engine View (Engine vs Engine) ----
        self.page_dual = QWidget(self)
        layout_dual = QVBoxLayout(self.page_dual)
        layout_dual.setContentsMargins(0, 0, 0, 0)
        layout_dual.setSpacing(6)

        # Telemetry Table Grid
        grid_dual = QGridLayout()
        grid_dual.setSpacing(4)
        
        lbl_col_metric = QLabel("Stat", self)
        lbl_col_metric.setStyleSheet("font-weight: bold;")
        lbl_col_w = QLabel("White Engine", self)
        lbl_col_w.setStyleSheet("font-weight: bold;")
        lbl_col_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_col_b = QLabel("Black Engine", self)
        lbl_col_b.setStyleSheet("font-weight: bold;")
        lbl_col_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        grid_dual.addWidget(lbl_col_metric, 0, 0)
        grid_dual.addWidget(lbl_col_w, 0, 1)
        grid_dual.addWidget(lbl_col_b, 0, 2)

        # Depth Row
        grid_dual.addWidget(QLabel("Depth:", self), 1, 0)
        self.lbl_depth_w = QLabel("0", self)
        self.lbl_depth_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_depth_b = QLabel("0", self)
        self.lbl_depth_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_dual.addWidget(self.lbl_depth_w, 1, 1)
        grid_dual.addWidget(self.lbl_depth_b, 1, 2)

        # Nodes Row
        grid_dual.addWidget(QLabel("Nodes:", self), 2, 0)
        self.lbl_nodes_w = QLabel("0", self)
        self.lbl_nodes_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nodes_b = QLabel("0", self)
        self.lbl_nodes_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_dual.addWidget(self.lbl_nodes_w, 2, 1)
        grid_dual.addWidget(self.lbl_nodes_b, 2, 2)

        # NPS Row
        grid_dual.addWidget(QLabel("NPS:", self), 3, 0)
        self.lbl_nps_w = QLabel("0", self)
        self.lbl_nps_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nps_b = QLabel("0", self)
        self.lbl_nps_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_dual.addWidget(self.lbl_nps_w, 3, 1)
        grid_dual.addWidget(self.lbl_nps_b, 3, 2)

        # Time Row
        grid_dual.addWidget(QLabel("Time:", self), 4, 0)
        self.lbl_time_w = QLabel("0ms", self)
        self.lbl_time_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time_b = QLabel("0ms", self)
        self.lbl_time_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_dual.addWidget(self.lbl_time_w, 4, 1)
        grid_dual.addWidget(self.lbl_time_b, 4, 2)

        # Score Row
        grid_dual.addWidget(QLabel("Score:", self), 5, 0)
        self.lbl_score_w = QLabel("+0.00", self)
        self.lbl_score_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_score_b = QLabel("+0.00", self)
        self.lbl_score_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_dual.addWidget(self.lbl_score_w, 5, 1)
        grid_dual.addWidget(self.lbl_score_b, 5, 2)

        layout_dual.addLayout(grid_dual)

        # Split PV Lines vertically to fit sidebar
        lbl_pv_w_title = QLabel("White Engine PV:", self)
        lbl_pv_w_title.setStyleSheet("font-weight: bold;")
        self.txt_pv_w = QTextEdit(self)
        self.txt_pv_w.setObjectName("pvTextArea")
        self.txt_pv_w.setReadOnly(True)
        self.txt_pv_w.setMinimumHeight(45)
        self.txt_pv_w.setMaximumHeight(65)

        lbl_pv_b_title = QLabel("Black Engine PV:", self)
        lbl_pv_b_title.setStyleSheet("font-weight: bold;")
        self.txt_pv_b = QTextEdit(self)
        self.txt_pv_b.setObjectName("pvTextArea")
        self.txt_pv_b.setReadOnly(True)
        self.txt_pv_b.setMinimumHeight(45)
        self.txt_pv_b.setMaximumHeight(65)

        layout_dual.addWidget(lbl_pv_w_title)
        layout_dual.addWidget(self.txt_pv_w, 1)
        layout_dual.addWidget(lbl_pv_b_title)
        layout_dual.addWidget(self.txt_pv_b, 1)

        self.stacked.addWidget(self.page_dual)

    def show_mode(self, is_dual: bool):
        self.stacked.setCurrentIndex(1 if is_dual else 0)

    def reset_displays(self):
        # Reset Page 0
        self.lbl_depth.setText("0")
        self.lbl_nodes.setText("0")
        self.lbl_nps.setText("0")
        self.lbl_time.setText("0ms")
        self.txt_pv.clear()
        
        # Reset Page 1
        self.lbl_depth_w.setText("0")
        self.lbl_depth_b.setText("0")
        self.lbl_nodes_w.setText("0")
        self.lbl_nodes_b.setText("0")
        self.lbl_nps_w.setText("0")
        self.lbl_nps_b.setText("0")
        self.lbl_time_w.setText("0ms")
        self.lbl_time_b.setText("0ms")
        self.lbl_score_w.setText("+0.00")
        self.lbl_score_b.setText("+0.00")
        self.txt_pv_w.clear()
        self.txt_pv_b.clear()
