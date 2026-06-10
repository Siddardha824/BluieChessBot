from PySide6.QtWidgets import QVBoxLayout, QLabel

from ..templates import StyledWidget

class HomePage(StyledWidget):
    def __init__(self, app_manager, parent = None):
        super().__init__("homePage", parent)

        self.manager = app_manager

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        label = QLabel("This is a test label")

        layout.addWidget(label)

