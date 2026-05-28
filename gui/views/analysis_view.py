# gui/views/analysis_view.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from gui.themes.theme_manager import theme_manager

class AnalysisView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self._init_ui()

    def _init_ui(self) -> None:
        # We set up a basic horizontal layout so that widgets can be injected or loaded
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # In Milestone 1, we will draw a simple notice.
        # GameController will clear and inject the actual widgets during Milestone 2 transition.
        placeholder_lbl = QLabel("Chess Game Workspace Placeholder")
        placeholder_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 16px; color: {self.theme.panel_text.name()};")
        placeholder_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(placeholder_lbl)

    def set_content_widgets(self, left_widget: QWidget, right_widget: QWidget) -> None:
        """Helper to dynamically populate the analysis workspace in Milestone 2."""
        # Clear the old placeholder
        for i in reversed(range(self.main_layout.count())): 
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        # Inject the active chess workspace layouts
        self.main_layout.addWidget(left_widget, 3)
        self.main_layout.addWidget(right_widget, 2)

    def update_theme(self) -> None:
        self.theme = theme_manager.get_theme()
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")
