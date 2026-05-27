# gui/panels/move_list_widget.py

from PySide6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PySide6.QtCore import Qt

class MoveListWidget(QWidget):
    def __init__(self, theme=None, parent=None):
        """
        Initializes the scrollable Move List Panel.
        Displays SAN moves split elegantly across White and Black columns.
        """
        super().__init__(parent)
        from gui.themes.default_theme import DefaultTheme
        self.theme = theme if theme is not None else DefaultTheme()
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 3 Columns: Move index (#), White moves, Black moves
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["#", "White", "Black"])
        
        # Align headers and set auto-stretching
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # UI Premium styling
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        # Hide standard Excel-like borders, gridlines, and headers
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        
        # Load colors dynamically from active theme to prevent hardcoding!
        bg_hex = self.theme.panel_background.name()
        text_hex = self.theme.panel_text.name()
        border_hex = self.theme.panel_border.name()
        
        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: {bg_hex}; color: {text_hex}; border: 1px solid {border_hex}; }}"
            f"QTableWidget::item {{ padding: 4px; font-weight: 500; border: none; }}"
        )
        
        layout.addWidget(self.table)

    def add_move(self, san_move: str) -> None:
        """
        Appends a SAN move to the history grid, automatically incrementing rows.
        """
        row_count = self.table.rowCount()
        
        # If table is empty, or the last row already has a Black move, insert a new row
        if row_count == 0 or self.table.item(row_count - 1, 2) is not None:
            self.table.insertRow(row_count)
            
            # 1. Move number
            move_num_item = QTableWidgetItem(f"{row_count + 1}.")
            move_num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            move_num_item.setForeground(self.theme.panel_text_muted)
            self.table.setItem(row_count, 0, move_num_item)
            
            # 2. White move
            white_item = QTableWidgetItem(san_move)
            white_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_count, 1, white_item)
        else:
            # 3. Black move (completing the last row)
            black_item = QTableWidgetItem(san_move)
            black_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_count - 1, 2, black_item)
            
        # Smooth scroll to ensure the latest moves are always visible
        self.table.scrollToBottom()

    def remove_last_move(self) -> None:
        """
        Removes the very last move from the SAN history grid.
        Handles both row deletion and black-to-white cell cell clearing.
        """
        row_count = self.table.rowCount()
        if row_count == 0:
            return
            
        # Check if the last row has a Black move
        if self.table.item(row_count - 1, 2) is not None:
            # Clear Black's move cell
            self.table.setItem(row_count - 1, 2, None)
        else:
            # Row only contains White's move, so delete the entire row
            self.table.removeRow(row_count - 1)

    def clear(self) -> None:
        """Clears all moves from the panel."""
        self.table.setRowCount(0)
