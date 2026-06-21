import chess
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from gui.utils import get_logger

logger = get_logger(__name__)

class MoveListWidget(QTableWidget):
    """
    Renders the game moves list in a clean 3-column table (Move Number, White, Black).
    Allows clicking on individual moves to view the board at that position.
    """
    move_selected = Signal(int)  # Emits the selected view_index

    def __init__(self, app_manager, parent=None):
        super().__init__(parent)
        self._manager = app_manager
        self._board_state = self._manager.board.session

        self.setup_ui()
        self._connect_signals()
        self.rebuild_list()

    def setup_ui(self):
        self.setObjectName("moveListTable")
        self.setColumnCount(3)
        self.horizontalHeader().setVisible(False)
        
        # Table configuration
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setShowGrid(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumWidth(80)
        
        # Horizontal headers styling
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Vertical headers hiding
        self.verticalHeader().setVisible(False)

    def _connect_signals(self):
        self._board_state.position_changed.connect(self.rebuild_list)
        self._board_state.view_changed.connect(self.update_highlight)
        self.cellClicked.connect(self._on_cell_clicked)

    def rebuild_list(self):
        """
        Rebuilds the table rows from the board's move stack.
        """
        logger.debug("Rebuilding move list from move stack.")
        self.clearContents()
        
        # Temporarily block signals to avoid recursion during rebuild
        self.blockSignals(True)
        
        moves = self._board_state.move_stack
        # Use a temporary chess board to generate SAN
        temp_board = chess.Board()
        # If the starting position is not standard FEN, initialize it properly
        starting_fen = self._board_state.starting_fen
        temp_board.set_fen(starting_fen)
        
        row_count = (len(moves) + 1) // 2
        self.setRowCount(row_count)
        
        for idx, move in enumerate(moves):
            row = idx // 2
            col = (idx % 2) + 1
            
            # Generate SAN representation for the move
            san = temp_board.san(move)
            temp_board.push(move)
            
            # Set move number label for column 0
            if col == 1:
                num_item = QTableWidgetItem(f"{row + 1}")
                num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                num_item.setForeground(Qt.GlobalColor.gray)
                self.setItem(row, 0, num_item)
                
            move_item = QTableWidgetItem(san)
            move_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, col, move_item)
            
        self.blockSignals(False)
        self.update_highlight()

    def update_highlight(self):
        """
        Highlights the move item matching the board's viewed index.
        """
        self.clearSelection()
        
        view_idx = self._board_state.view_index
        if view_idx <= 0:
            return
            
        move_idx = view_idx - 1
        row = move_idx // 2
        col = (move_idx % 2) + 1
        
        item = self.item(row, col)
        if item:
            self.setCurrentItem(item)
            item.setSelected(True)

    def _on_cell_clicked(self, row: int, column: int):
        if column == 0:
            return
            
        move_idx = row * 2 + (column - 1)
        moves_len = len(self._board_state.move_stack)
        
        if move_idx < moves_len:
            view_index = move_idx + 1
            logger.info("Move history click: selecting view index %s", view_index)
            self.move_selected.emit(view_index)
