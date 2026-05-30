# gui/widgets/engine_status_widget.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from gui.views.analysis.styles.analysis_styles import get_panel_title_style, get_dot_indicator_style

class EngineStatusWidget(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        self.lbl_title = QLabel("Engine: Not Available")
        self.lbl_title.setStyleSheet(get_panel_title_style(self.theme))
        
        self.dot_indicator = QLabel()
        self.dot_indicator.setFixedSize(8, 8)
        self.dot_indicator.setStyleSheet("background-color: #8B0000; border-radius: 4px;") # Start disconnected (red dot)
        
        layout.addWidget(self.lbl_title)
        layout.addStretch()
        layout.addWidget(self.dot_indicator)

    def set_status(self, name: str, status: str, connection_status: str) -> None:
        """Sets the active status and details of the engine, repainting indicators reactively."""
        if connection_status == "Disconnected":
            self.lbl_title.setText("Engine: Not Available")
            self.dot_indicator.setStyleSheet("background-color: #8B0000; border-radius: 4px;") # Dark red dot
        else:
            self.lbl_title.setText(f"Engine: {name}")
            if status == "Searching":
                self.dot_indicator.setStyleSheet("background-color: #3498DB; border-radius: 4px;") # Glowing blue dot
            else:
                self.dot_indicator.setStyleSheet("background-color: #2ECC71; border-radius: 4px;") # Glowing green dot

    def update_theme(self, theme) -> None:
        self.theme = theme
        self.lbl_title.setStyleSheet(get_panel_title_style(self.theme))
