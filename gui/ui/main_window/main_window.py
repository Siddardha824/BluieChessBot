from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout
)

from PySide6.QtCore import Qt

from gui.ui.board import ChessBoard


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bluie Chess")
        self.resize(1200, 700)

        self.setup_ui()

    def setup_ui(self):

        container = QWidget()

        layout = QVBoxLayout()

        self.board = ChessBoard()

        layout.addWidget(
            self.board,
            alignment=Qt.AlignCenter
        )

        container.setLayout(layout)

        self.setCentralWidget(container)