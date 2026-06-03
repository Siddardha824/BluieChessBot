# gui/widgets/engine_control_widget.py

from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QLabel, QPushButton, QSpinBox, QCheckBox, QFrame
from PySide6.QtCore import Qt, Signal

from .themed_widget import ThemedWidget
from gui.views.analysis.styles.analysis_styles import (
    get_control_label_style, get_input_field_style, get_checkbox_style,
    get_new_search_button_style, get_stop_button_style, get_quick_secondary_button_style
)

class EngineControlWidget(ThemedWidget):
    # Signals generated when user clicks or triggers control options
    start_search = Signal(dict)
    stop_search = Signal()
    clear_board = Signal()
    flip_board = Signal()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 1. Search Configuration Grid
        config_grid = QGridLayout()
        config_grid.setSpacing(8)
        
        # Max Depth Option
        lbl_depth = QLabel("Max Depth")
        lbl_depth.setStyleSheet(get_control_label_style(self.theme))
        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(1, 100)
        self.spin_depth.setValue(15)
        self.spin_depth.setStyleSheet(get_input_field_style(self.theme))
        
        # Max Nodes Option (0 means infinite)
        lbl_nodes = QLabel("Max Nodes")
        lbl_nodes.setStyleSheet(get_control_label_style(self.theme))
        self.spin_nodes = QSpinBox()
        self.spin_nodes.setRange(0, 1000000000)
        self.spin_nodes.setSingleStep(1000000)
        self.spin_nodes.setValue(0)
        self.spin_nodes.setSpecialValueText("Infinite")
        self.spin_nodes.setStyleSheet(get_input_field_style(self.theme))
        
        # Move Time Option (0 means infinite)
        lbl_time = QLabel("Move Time (ms)")
        lbl_time.setStyleSheet(get_control_label_style(self.theme))
        self.spin_time = QSpinBox()
        self.spin_time.setRange(0, 3600000)
        self.spin_time.setSingleStep(1000)
        self.spin_time.setValue(0)
        self.spin_time.setSpecialValueText("Infinite")
        self.spin_time.setStyleSheet(get_input_field_style(self.theme))
        
        # Infinite Search Toggle
        self.chk_infinite = QCheckBox("Infinite Search")
        self.chk_infinite.setStyleSheet(get_checkbox_style(self.theme))
        self.chk_infinite.toggled.connect(self._on_infinite_toggled)
        
        config_grid.addWidget(lbl_depth, 0, 0)
        config_grid.addWidget(self.spin_depth, 1, 0)
        config_grid.addWidget(lbl_nodes, 0, 1)
        config_grid.addWidget(self.spin_nodes, 1, 1)
        
        config_grid.addWidget(lbl_time, 2, 0)
        config_grid.addWidget(self.spin_time, 3, 0)
        config_grid.addWidget(self.chk_infinite, 3, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        layout.addLayout(config_grid)
        
        # Divider Line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet(f"background-color: {self.theme.panel_border.name()}; max-height: 1px; border: none;")
        layout.addWidget(divider)
        
        # 2. Action Buttons 2x2 Grid
        btn_grid = QGridLayout()
        btn_grid.setSpacing(8)
        
        self.btn_new_search = QPushButton("🔍 New Search")
        self.btn_new_search.setStyleSheet(get_new_search_button_style())
        self.btn_new_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_search.clicked.connect(self._on_new_search_clicked)
        
        self.btn_stop = QPushButton("⏸ Stop")
        self.btn_stop.setStyleSheet(get_stop_button_style())
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.stop_search.emit)
        
        self.btn_clear = QPushButton("⟳ Clear Board")
        self.btn_clear.setStyleSheet(get_quick_secondary_button_style(self.theme))
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_board.emit)
        
        self.btn_flip = QPushButton("⇄ Flip Board")
        self.btn_flip.setStyleSheet(get_quick_secondary_button_style(self.theme))
        self.btn_flip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_flip.clicked.connect(self.flip_board.emit)
        
        btn_grid.addWidget(self.btn_new_search, 0, 0)
        btn_grid.addWidget(self.btn_stop, 0, 1)
        btn_grid.addWidget(self.btn_clear, 1, 0)
        btn_grid.addWidget(self.btn_flip, 1, 1)
        
        layout.addLayout(btn_grid)

    def _on_infinite_toggled(self, checked: bool) -> None:
        """Toggles enabling of other search parameters on infinite mode."""
        self.spin_depth.setDisabled(checked)
        self.spin_nodes.setDisabled(checked)
        self.spin_time.setDisabled(checked)

    def _on_new_search_clicked(self) -> None:
        """Emits start_search signal with active configurations."""
        self.start_search.emit(self.get_search_params())

    def get_search_params(self) -> dict:
        """
        Gathers and returns configured search parameters from inputs.
        
        Returns:
            dict: Search configuration dict with keys: 'depth', 'movetime', 'nodes', 'infinite'.
        """
        infinite = self.chk_infinite.isChecked()
        if infinite:
            return {
                "depth": None,
                "movetime": None,
                "nodes": None,
                "infinite": True
            }
        
        depth = self.spin_depth.value()
        nodes = self.spin_nodes.value()
        movetime = self.spin_time.value()
        
        return {
            "depth": depth if depth > 0 else None,
            "movetime": movetime if movetime > 0 else None,
            "nodes": nodes if nodes > 0 else None,
            "infinite": False
        }

    def apply_theme(self) -> None:
        """Repaints component colors on active theme change."""
        
        # Update stylesheet configurations dynamically
        self.spin_depth.setStyleSheet(get_input_field_style(self.theme))
        self.spin_nodes.setStyleSheet(get_input_field_style(self.theme))
        self.spin_time.setStyleSheet(get_input_field_style(self.theme))
        self.chk_infinite.setStyleSheet(get_checkbox_style(self.theme))
        self.btn_clear.setStyleSheet(get_quick_secondary_button_style(self.theme))
        self.btn_flip.setStyleSheet(get_quick_secondary_button_style(self.theme))
