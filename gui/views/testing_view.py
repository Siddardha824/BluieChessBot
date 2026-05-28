# gui/views/testing_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from gui.themes.theme_manager import theme_manager

class TestingView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Engine Testing & Perft Diagnostics")
        title.setStyleSheet(f"font-family: 'Outfit'; font-size: 18px; font-weight: bold; color: {self.theme.console_in.name()};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("Automated testing suite, visual Perft divide, and interactive UCI command debug terminal.")
        desc.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; color: {self.theme.panel_text.name()};")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

    def update_theme(self) -> None:
        self.theme = theme_manager.get_theme()
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")
