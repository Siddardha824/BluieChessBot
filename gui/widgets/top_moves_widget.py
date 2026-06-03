# gui/widgets/top_moves_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt
from gui.views.analysis.styles.analysis_styles import get_section_header_style, get_table_header_style, get_table_style
from .themed_widget import ThemedWidget

class TopMovesWidget(ThemedWidget):
    def __init__(self, theme, initial_top_moves=None, parent=None):
        self.initial_top_moves = initial_top_moves
        super().__init__(theme, parent)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        top_moves_hdr = QLabel("Top Moves")
        top_moves_hdr.setStyleSheet(get_section_header_style(self.theme))
        
        self.top_moves_table = QTableWidget()
        self.top_moves_table.setColumnCount(5)
        self.top_moves_table.setHorizontalHeaderLabels(["Move", "Eval", "Depth", "Nodes", "%"])
        self.top_moves_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.top_moves_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.top_moves_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.top_moves_table.setRowCount(5)
        
        self.top_moves_table.horizontalHeader().setStyleSheet(get_table_header_style(self.theme))
        self.top_moves_table.verticalHeader().hide()
        self.top_moves_table.setShowGrid(False)
        self.top_moves_table.setStyleSheet(get_table_style(self.theme))
        
        layout.addWidget(top_moves_hdr)
        layout.addWidget(self.top_moves_table)
        
        self.clear()

    def populate(self, moves_list) -> None:
        """Populates the custom QTableWidget top moves list rows."""
        self.top_moves_table.setRowCount(len(moves_list))
        for row, move_data in enumerate(moves_list):
            for col, text in enumerate(move_data):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.top_moves_table.setItem(row, col, item)

    def clear(self) -> None:
        """Resets the top moves table back to baseline placeholders."""
        if self.initial_top_moves is not None:
            self.populate(self.initial_top_moves)
        else:
            clean_moves = [
                ("-", "-", "-", "-", "-"),
                ("-", "-", "-", "-", "-"),
                ("-", "-", "-", "-", "-"),
                ("-", "-", "-", "-", "-"),
                ("-", "-", "-", "-", "-")
            ]
            self.populate(clean_moves)

    def apply_theme(self) -> None:
        self.top_moves_table.horizontalHeader().setStyleSheet(get_table_header_style(self.theme))
        self.top_moves_table.setStyleSheet(get_table_style(self.theme))
