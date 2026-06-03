from PySide6.QtWidgets import QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal

from .themed_widget import ThemedWidget
from gui.views.analysis.styles.analysis_styles import get_toolbar_button_style

class BoardNavigationWidget(ThemedWidget):
    # Signals triggered when user clicks on board control buttons
    undo_move_to_first = Signal()
    undo_move = Signal()
    redo_move = Signal()
    redo_move_to_last = Signal()
    flip_board = Signal()
    play = Signal()

    def setup_ui(self):

        # Board Navigation Toolbar
        nav_toolbar = QHBoxLayout(self)
        nav_toolbar.setSpacing(5)
        nav_toolbar.addStretch()
        
        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")
        self.btn_rotate = QPushButton("⟳")
        self.btn_play = QPushButton("▶")

        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_rotate, self.btn_play]:
            btn.setStyleSheet(get_toolbar_button_style(self.theme))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            nav_toolbar.addWidget(btn)
            
        nav_toolbar.addStretch()

    def connect_signals(self) -> None:
        self.btn_first.clicked.connect(self.undo_move_to_first.emit)
        self.btn_prev.clicked.connect(self.undo_move.emit)
        self.btn_next.clicked.connect(self.redo_move.emit)
        self.btn_last.clicked.connect(self.redo_move_to_last.emit)
        self.btn_rotate.clicked.connect(self.flip_board.emit)
        self.btn_play.clicked.connect(self.play.emit)
        
    def apply_theme(self):
        # Re-apply toolbar styles dynamically
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_rotate, self.btn_play]:
            btn.setStyleSheet(get_toolbar_button_style(self.theme))

