"""
Move-history view for displaying and navigating a linear chess game.

This module provides the MoveHistoryPanel view widget. It renders a flat list
of SAN moves and emits navigation intents without depending on game state or
the application coordinator.
"""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from gui.ui.core import StyledWidget


class MoveHistoryPanel(StyledWidget):
    """
    Provide a move-history view that emits navigation intents without owning game state.

    Moves are supplied as a flat, chronological list: White's first move has
    ply index ``0``, Black's reply has ply index ``1``, and so on. Selecting a
    move or using navigation controls emits the target ply index for the
    coordinator to apply to the board model.

    Styling hooks: ``#moveHistoryPanel``, ``#moveHistoryTable``,
    ``#moveHistoryEmpty``, and ``#moveHistoryNavigation``.

    Signals:
        move_selected (Signal[int]): Emitted when the user selects a SAN move.
        first_move_requested (Signal): Emitted when the user requests the first move.
        previous_move_requested (Signal): Emitted when the user requests the previous move.
        next_move_requested (Signal): Emitted when the user requests the next move.
        last_move_requested (Signal): Emitted when the user requests the last move.
    """

    # Emitted when the user selects a SAN move. Payload: zero-based ply index (int).
    move_selected = Signal(int)

    # Emitted when the user requests navigation to the first recorded move.
    first_move_requested = Signal()

    # Emitted when the user requests navigation to the previous recorded move.
    previous_move_requested = Signal()

    # Emitted when the user requests navigation to the next recorded move.
    next_move_requested = Signal()

    # Emitted when the user requests navigation to the final recorded move.
    last_move_requested = Signal()

    # --- UI Initialization ---

    def __init__(self, parent):
        """Initialize the standalone move-history panel.

        Args:
            parent: The parent QWidget.
        """
        super().__init__(object_name="moveHistoryPanel", parent=parent)

    # --- Layout Setup ---

    def _setup_ui(self):
        """Build the compact move table, empty state, and navigation controls."""
        self._moves: list[str] = []
        self._current_ply: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Move History")
        title.setObjectName("moveHistoryTitle")
        layout.addWidget(title)

        self.empty_label = QLabel("No moves yet")
        self.empty_label.setObjectName("moveHistoryEmpty")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)

        self.move_table = QTableWidget(0, 3)
        self.move_table.setObjectName("moveHistoryTable")
        self.move_table.setHorizontalHeaderLabels(["#", "White", "Black"])
        self.move_table.verticalHeader().hide()
        self.move_table.horizontalHeader().setStretchLastSection(True)
        self.move_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.move_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.move_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.move_table.setShowGrid(False)
        self.move_table.setVisible(False)
        layout.addWidget(self.move_table, 1)

        navigation = QHBoxLayout()
        navigation.setObjectName("moveHistoryNavigation")
        navigation.setSpacing(4)
        self.first_button = QPushButton("|<")
        self.previous_button = QPushButton("<")
        self.next_button = QPushButton(">")
        self.last_button = QPushButton(">|")
        for button in (self.first_button, self.previous_button, self.next_button, self.last_button):
            button.setObjectName("moveHistoryNavButton")
            button.setEnabled(False)
            navigation.addWidget(button)
        layout.addLayout(navigation)

        self.move_table.itemClicked.connect(self._on_item_clicked)
        self.first_button.clicked.connect(self.first_move_requested.emit)
        self.previous_button.clicked.connect(self.previous_move_requested.emit)
        self.next_button.clicked.connect(self.next_move_requested.emit)
        self.last_button.clicked.connect(self.last_move_requested.emit)

    # --- Public Slots (State Updates) ---

    @Slot(list, object)
    def set_moves(self, moves: list[str], current_ply: int | None = None) -> None:
        """Replace displayed SAN moves and select the active zero-based ply.

        Args:
            moves: Chronological SAN strings, beginning with White's first move.
            current_ply: The zero-based ply to highlight, or None to clear selection.
        """
        self._moves = list(moves)
        self._current_ply = current_ply if current_ply is not None and 0 <= current_ply < len(self._moves) else None

        self.move_table.setUpdatesEnabled(False)
        self.move_table.clearContents()
        self.move_table.setRowCount((len(self._moves) + 1) // 2)
        for ply, san in enumerate(self._moves):
            row, column = divmod(ply, 2)
            if column == 0:
                number_item = QTableWidgetItem(f"{row + 1}.")
                number_item.setFlags(number_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.move_table.setItem(row, 0, number_item)
            move_item = QTableWidgetItem(san)
            move_item.setData(Qt.ItemDataRole.UserRole, ply)
            self.move_table.setItem(row, column + 1, move_item)

        self.move_table.setUpdatesEnabled(True)
        self.empty_label.setVisible(not self._moves)
        self.move_table.setVisible(bool(self._moves))
        self._select_current_move()
        self._update_navigation_state()

    @Slot(object)
    def set_current_ply(self, current_ply: int | None) -> None:
        """Highlight an active ply without emitting a user-selection signal.

        Args:
            current_ply: The zero-based ply to highlight, or None to clear selection.
        """
        self._current_ply = current_ply if current_ply is not None and 0 <= current_ply < len(self._moves) else None
        self._select_current_move()
        self._update_navigation_state()

    # --- Private Helpers ---

    def _select_current_move(self) -> None:
        """Select and reveal the table cell matching the current ply."""
        self.move_table.clearSelection()
        if self._current_ply is None:
            return
        row, column = divmod(self._current_ply, 2)
        item = self.move_table.item(row, column + 1)
        if item is not None:
            self.move_table.setCurrentItem(item)
            self.move_table.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)

    def _update_navigation_state(self) -> None:
        """Enable navigation only where a requested move can exist."""
        has_moves = bool(self._moves)
        at_first = self._current_ply in (None, 0)
        at_last = self._current_ply == len(self._moves) - 1
        self.first_button.setEnabled(has_moves and not at_first)
        self.previous_button.setEnabled(has_moves and not at_first)
        self.next_button.setEnabled(has_moves and not at_last)
        self.last_button.setEnabled(has_moves and not at_last)

    # --- Private Slots (User Intents) ---

    def _on_item_clicked(self, item: QTableWidgetItem) -> None:
        """Translate a clicked SAN cell into a ply-selection intent.

        Args:
            item: The table item selected by the user.
        """
        ply = item.data(Qt.ItemDataRole.UserRole)
        if ply is not None:
            self.move_selected.emit(ply)

        
