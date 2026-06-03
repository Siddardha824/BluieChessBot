# gui/views/analysis/sections/board_section.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from gui.board.board_widget import ChessBoard
from gui.widgets import BoardNavigationWidget
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
        self.nav_toolbar = BoardNavigationWidget(self.theme)
        board_layout.addWidget(self.nav_toolbar)

    def update_theme(self, theme):
        self.theme = theme
        self.board.theme = theme
        self.board.update()
        self.board_title.setStyleSheet(get_panel_title_style(self.theme))
        self.nav_toolbar.update_theme(self.theme)
