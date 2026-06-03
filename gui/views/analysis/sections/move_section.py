# gui/views/analysis/sections/move_section.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal

from gui.widgets import MoveListWidget
from gui.views.analysis.styles.analysis_styles import (
    get_tab_moves_active_style, get_tab_inactive_style, get_icon_button_style
)

class MoveSection(QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setObjectName("MoveLogCard")
        self._init_ui()

    def _init_ui(self):
        move_log_layout = QVBoxLayout(self)
        move_log_layout.setContentsMargins(15, 15, 15, 15)
        move_log_layout.setSpacing(10)
        
        # # Tabs layout selector: Moves | Table | Book
        # tabs_box = QHBoxLayout()
        # tabs_box.setSpacing(10)
        
        # self.btn_tab_moves = QPushButton("Moves")
        # self.btn_tab_moves.setStyleSheet(get_tab_moves_active_style(self.theme))
        
        # self.btn_tab_table = QPushButton("Table")
        # self.btn_tab_table.setStyleSheet(get_tab_inactive_style(self.theme))
        
        # self.btn_tab_book = QPushButton("Book")
        # self.btn_tab_book.setStyleSheet(get_tab_inactive_style(self.theme))
        
        # tabs_box.addWidget(self.btn_tab_moves)
        # tabs_box.addWidget(self.btn_tab_table)
        # tabs_box.addWidget(self.btn_tab_book)
        # tabs_box.addStretch()
        # move_log_layout.addLayout(tabs_box)
        
        # Inject MoveListWidget in active workspace
        self.move_list = MoveListWidget(theme=self.theme)
        move_log_layout.addWidget(self.move_list, stretch=1)
        
        # # Icons Row: Graph | Target | Copy | Download
        # icons_row = QHBoxLayout()
        # icons_row.setSpacing(12)
        
        # self.btn_icon_graph = QPushButton("📈")
        # self.btn_icon_target = QPushButton("🎯")
        # self.btn_icon_copy = QPushButton("📋")
        # self.btn_icon_download = QPushButton("💾")
        
        # for btn in [self.btn_icon_graph, self.btn_icon_target, self.btn_icon_copy, self.btn_icon_download]:
        #     btn.setStyleSheet(get_icon_button_style(self.theme))
        #     btn.setCursor(Qt.CursorShape.PointingHandCursor)
        #     icons_row.addWidget(btn)
            
        # icons_row.addStretch()
        # move_log_layout.addLayout(icons_row)

    def update_theme(self, theme):
        self.theme = theme
        self.move_list.update_theme(self.theme)
        
        # # Re-apply stylesheets
        # self.btn_tab_moves.setStyleSheet(get_tab_moves_active_style(self.theme))
        # self.btn_tab_table.setStyleSheet(get_tab_inactive_style(self.theme))
        # self.btn_tab_book.setStyleSheet(get_tab_inactive_style(self.theme))
        
        # for btn in [self.btn_icon_graph, self.btn_icon_target, self.btn_icon_copy, self.btn_icon_download]:
        #     btn.setStyleSheet(get_icon_button_style(self.theme))
