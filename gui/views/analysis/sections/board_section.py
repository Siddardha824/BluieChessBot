# gui/views/analysis/sections/board_section.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from gui.board.board_widget import ChessBoard
from gui.views.analysis.styles.analysis_styles import get_panel_title_style, get_toolbar_button_style

class BoardSection(QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setObjectName("BoardPanel")
        self._init_ui()

    def _init_ui(self):
        board_layout = QVBoxLayout(self)
        board_layout.setContentsMargins(15, 15, 15, 15)
        board_layout.setSpacing(10)

        self.board_title = QLabel("Board")
        self.board_title.setStyleSheet(get_panel_title_style(self.theme))
        board_layout.addWidget(self.board_title)
        
        # Center ChessBoard widget
        self.board = ChessBoard(theme=self.theme)
        board_layout.addWidget(self.board, stretch=1)
        
        # Bottom Navigation Toolbar
        nav_toolbar = QHBoxLayout()
        nav_toolbar.setSpacing(5)
        nav_toolbar.addStretch()
        
        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")
        self.btn_add = QPushButton("+")
        self.btn_del = QPushButton("-")
        self.btn_rotate = QPushButton("⟳")
        self.btn_play = QPushButton("▶")
        
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_add, self.btn_del, self.btn_rotate, self.btn_play]:
            btn.setStyleSheet(get_toolbar_button_style(self.theme))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            nav_toolbar.addWidget(btn)
            
        nav_toolbar.addStretch()
        board_layout.addLayout(nav_toolbar)

    def update_theme(self, theme):
        self.theme = theme
        self.board.theme = theme
        self.board.update()
        self.board_title.setStyleSheet(get_panel_title_style(self.theme))
        
        # Re-apply toolbar styles dynamically
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_add, self.btn_del, self.btn_rotate, self.btn_play]:
            btn.setStyleSheet(get_toolbar_button_style(self.theme))
