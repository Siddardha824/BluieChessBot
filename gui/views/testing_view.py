# gui/views/testing_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from gui.themes.theme_manager import theme_manager
from gui.core.app_state import app_state
from gui.board.board_widget import ChessBoard
from gui.models.board_state import BoardState
from gui.board.highlights import HighlightManager
from gui.models.move import Move

class TestingView(QWidget):
    def __init__(self, engine_manager=None, parent=None):
        """
        Initializes the C++ Chess Engine Perft & Divide visual debugger.
        Exposes FEN testing fields, custom depth spinners, and a sortable QTableWidget
        side-by-side with a fully synchronized mini-chessboard.
        """
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self.engine_manager = engine_manager
        
        # Local mini-board state models (fully decoupled from Analysis)
        self.board_state = BoardState()
        self.highlight_manager = HighlightManager()
        
        self._init_ui()
        self.setup_engine_bindings()

        # Connect to theme changes reactively
        app_state.signals.theme_changed.connect(lambda: self.update_theme())

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        # Apply parent background
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")

        # ==========================================
        # 1. HEADER TELEMETRY TITLE
        # ==========================================
        header = QVBoxLayout()
        header.setSpacing(5)
        title = QLabel("PERFT DIVIDE DEBUGGER")
        title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 20px; font-weight: 800; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        desc = QLabel("Assert legal move generator correctness by recursively walking search paths and auditing subnode discrepancies.")
        desc.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 12px; font-weight: 500; "
            f"color: {self.theme.panel_text_muted.name()};"
        )
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # ==========================================
        # 2. MAIN GRID LAYOUT
        # ==========================================
        main_layout = QHBoxLayout()
        main_layout.setSpacing(25)

        # ------------------------------------------
        # A. LEFT SECTION: CONFIG & MINI-BOARD
        # ------------------------------------------
        left_card = QFrame()
        left_card.setObjectName("ConfigCard")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)

        config_title = QLabel("TESTING POSITION SETUP")
        config_title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 13px; font-weight: 700; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        left_layout.addWidget(config_title)

        # FEN Input
        fen_lbl = QLabel("TEST POSITION FEN")
        fen_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 10px; font-weight: bold; color: {self.theme.panel_text_muted.name()}; text-transform: uppercase;")
        self.fen_input = QLineEdit("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.fen_input.textChanged.connect(self._handle_fen_changed)
        left_layout.addWidget(fen_lbl)
        left_layout.addWidget(self.fen_input)

        # Depth Spinner & Buttons
        ctrl_box = QHBoxLayout()
        ctrl_box.setSpacing(15)

        depth_box = QVBoxLayout()
        depth_box.setSpacing(5)
        depth_lbl = QLabel("DEPTH")
        depth_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 10px; font-weight: bold; color: {self.theme.panel_text_muted.name()}; text-transform: uppercase;")
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 6)
        self.depth_spin.setValue(3)
        depth_box.addWidget(depth_lbl)
        depth_box.addWidget(self.depth_spin)
        ctrl_box.addLayout(depth_box, 1)

        # Actions
        self.run_btn = QPushButton("RUN DIVIDE")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self._handle_run_divide)
        self.run_btn.setFixedHeight(38)
        ctrl_box.addWidget(self.run_btn, 2)
        left_layout.addLayout(ctrl_box)

        # Decoupled mini-chessboard QWidget
        self.board = ChessBoard(theme=self.theme)
        self.board.set_models(self.board_state, self.highlight_manager)
        self.board.setFixedSize(300, 300)
        
        # Center the mini board
        board_container = QHBoxLayout()
        board_container.addStretch()
        board_container.addWidget(self.board)
        board_container.addStretch()
        left_layout.addLayout(board_container)
        left_layout.addStretch()

        # ------------------------------------------
        # B. RIGHT SECTION: DIVIDE RESULT GRID
        # ------------------------------------------
        right_card = QFrame()
        right_card.setObjectName("DivideCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(25, 25, 25, 25)
        right_layout.setSpacing(15)

        divide_title_layout = QHBoxLayout()
        divide_title = QLabel("DIVIDE MOVE LIST")
        divide_title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 13px; font-weight: 700; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        self.total_lbl = QLabel("Total: -")
        self.total_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: {self.theme.console_out.name()};")
        divide_title_layout.addWidget(divide_title)
        divide_title_layout.addStretch()
        divide_title_layout.addWidget(self.total_lbl)
        right_layout.addLayout(divide_title_layout)

        # Sortable grid
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Move", "Subnode Count"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.itemClicked.connect(self._handle_row_clicked)

        # Header stretch
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Style table headers and cells
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        right_layout.addWidget(self.table)

        main_layout.addWidget(left_card, 3)
        main_layout.addWidget(right_card, 4)
        layout.addLayout(main_layout)
        
        self.update_stylesheets()

    def setup_engine_bindings(self) -> None:
        """Wires standard telemetry signals from EngineManager directly to the grid."""
        if self.engine_manager:
            self.engine_manager.divide_start.connect(self._handle_divide_start)
            self.engine_manager.divide_move.connect(self._handle_divide_move)
            self.engine_manager.divide_total.connect(self._handle_divide_total)

    def _handle_fen_changed(self, text: str) -> None:
        """Safely parses custom positions onto the mini-board."""
        try:
            self.board_state.set_fen(text)
            self.highlight_manager.clear()
            self.board.update()
        except Exception:
            pass

    def _handle_run_divide(self) -> None:
        """Sends FEN position and triggers C++ divide search."""
        if self.engine_manager and self.engine_manager.engine_status != "Disconnected":
            # Clear old grid rows
            self.table.setSortingEnabled(False)
            self.table.setRowCount(0)
            self.total_lbl.setText("Running...")
            self.highlight_manager.clear()
            self.board.update()

            fen = self.fen_input.text().strip()
            depth = self.depth_spin.value()

            # Configure positions FEN
            self.engine_manager.send_command(f"position fen {fen}")
            self.engine_manager.send_command(f"bluie-debug divide {depth}")

    def _handle_divide_start(self, depth: int) -> None:
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

    def _handle_divide_move(self, move_part: str, nodes: int) -> None:
        """Appends subnodes row into the sortable table grid."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        move_item = QTableWidgetItem(move_part)
        move_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        move_item.setData(Qt.ItemDataRole.UserRole, move_part)

        nodes_item = QTableWidgetItem(f"{nodes:,}")
        nodes_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # Store integer data inside standard UserRole to ensure numeric sorting works perfectly
        nodes_item.setData(Qt.ItemDataRole.UserRole, nodes)

        self.table.setItem(row, 0, move_item)
        self.table.setItem(row, 1, nodes_item)

    def _handle_divide_total(self, total: int) -> None:
        self.total_lbl.setText(f"Total: {total:,} nodes")
        self.table.setSortingEnabled(True)

    def _handle_row_clicked(self, item: QTableWidgetItem) -> None:
        """
        Parses the clicked row move coordinate (e.g. 'e2e4') and highlights
        its path onto the mini-board for instant visual diagnostics.
        """
        row = item.row()
        move_item = self.table.item(row, 0)
        if not move_item:
            return

        move_str = move_item.text().strip()
        if len(move_str) >= 4:
            try:
                from_coord = move_str[0:2]
                to_coord = move_str[2:4]
                
                # Convert coords to board indexes (e.g. e2 -> index)
                from_idx = self.board_state.coordinate_to_index(from_coord)
                to_idx = self.board_state.coordinate_to_index(to_coord)

                if from_idx is not None and to_idx is not None:
                    self.highlight_manager.set_last_move(from_idx, to_idx)
                    self.board.update()
            except Exception:
                pass

    def update_stylesheets(self) -> None:
        bg_hex = self.theme.panel_background.name()
        border_hex = self.theme.panel_border.name()
        text_hex = self.theme.panel_text.name()
        button_bg = self.theme.dark_square.name()
        button_hover = self.theme.light_square.name()

        self.setStyleSheet(
            f"QWidget {{ background-color: {bg_hex}; }}"
            f"QFrame#ConfigCard, QFrame#DivideCard {{"
            f"  background-color: rgba(22, 17, 38, 0.25);"
            f"  border: 1px solid {border_hex};"
            f"  border-radius: 6px;"
            f"}}"
            f"QLineEdit, QSpinBox {{"
            f"  background-color: rgba(0, 0, 0, 0.3);"
            f"  color: {text_hex};"
            f"  border: 1px solid {border_hex};"
            f"  border-radius: 4px;"
            f"  padding: 8px;"
            f"  font-family: 'Outfit';"
            f"  font-size: 12px;"
            f"}}"
            f"QPushButton {{"
            f"  background-color: {button_bg};"
            f"  color: #FFFFFF;"
            f"  border: none;"
            f"  border-radius: 4px;"
            f"  font-family: 'Outfit';"
            f"  font-size: 12px;"
            f"  font-weight: bold;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {button_hover};"
            f"  color: {button_bg};"
            f"}}"
            f"QTableWidget {{"
            f"  background-color: rgba(0, 0, 0, 0.2);"
            f"  color: {text_hex};"
            f"  border: 1px solid {border_hex};"
            f"  font-family: 'Outfit';"
            f"  font-size: 12px;"
            f"  gridline-color: transparent;"
            f"}}"
            f"QHeaderView::section {{"
            f"  background-color: rgba(22, 17, 38, 0.5);"
            f"  color: {self.theme.console_in.name()};"
            f"  border: 1px solid {border_hex};"
            f"  font-family: 'Outfit';"
            f"  font-size: 11px;"
            f"  font-weight: bold;"
            f"  padding: 6px;"
            f"}}"
        )
        self.board.theme = self.theme
        self.board.update()

    def update_theme(self) -> None:
        """Reactive theme updating."""
        self.theme = theme_manager.get_theme()
        self.update_stylesheets()
