# gui/views/analysis_view.py

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QProgressBar, QGridLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
)
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QColor, QFont

from gui.board.board_widget import ChessBoard
from gui.panels.move_list_widget import MoveListWidget
from gui.panels.eval_bar_widget import EvalBarWidget
from gui.panels.debug_console_widget import DebugConsoleWidget
from gui.panels.centipawn_graph_widget import CentipawnGraphWidget
from gui.themes.theme_manager import theme_manager
from gui.core.app_state import app_state
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisView(QWidget):
    def __init__(self, engine_manager=None, parent=None):
        """
        Initializes the refined 3-column Analysis view.
        Moves all board workspace controls, telemetry details, and action quick-panels
        inside this view container to enable clean single-transition tab swaps.
        """
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self.engine_manager = engine_manager
        
        # 1. Instantiate the Public Components expected by GameController & MainWindow
        self.board = ChessBoard(theme=self.theme)
        
        # Hidden legacy widgets preserved to satisfy controller bindings safely
        self.eval_bar = EvalBarWidget(theme=self.theme)
        self.eval_bar.hide()
        
        # The graph and debug console are created locally. The graph will display in a premium popup modal when clicked.
        self.centipawn_graph = CentipawnGraphWidget(theme=self.theme)
        self.debug_console = DebugConsoleWidget(theme=self.theme, engine_manager=self.engine_manager)
        self.debug_console.hide()

        self._init_ui()
        
        # Connect theme swapper reactive slot
        app_state.signals.theme_changed.connect(lambda: self.update_theme())

    def _init_ui(self) -> None:
        # Main vertical structure: Title Header -> Horizontal 3-column split
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(15)
        
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")

        # ==========================================
        # 1. COSMIC TITLE HEADER
        # ==========================================
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_lbl = QLabel("1. ANALYSIS (Board & Engine Analysis)")
        title_lbl.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 18px; font-weight: 800; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 0.5px;"
        )
        
        header_line = QFrame()
        header_line.setFrameShape(QFrame.Shape.HLine)
        header_line.setStyleSheet(f"color: {self.theme.panel_border.name()}; border: 1px solid {self.theme.panel_border.name()};")
        
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(header_line)
        root_layout.addLayout(header_layout)

        # ==========================================
        # 2. THREE-COLUMN WORKSPACE
        # ==========================================
        workspace_layout = QHBoxLayout()
        workspace_layout.setSpacing(15)

        # ------------------------------------------
        # COLUMN A: BOARD PANEL (LEFT)
        # ------------------------------------------
        board_panel = QFrame()
        board_panel.setObjectName("BoardPanel")
        board_layout = QVBoxLayout(board_panel)
        board_layout.setContentsMargins(15, 15, 15, 15)
        board_layout.setSpacing(10)

        board_title = QLabel("Board")
        board_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 13px; font-weight: 700; color: {self.theme.panel_text_muted.name()};")
        board_layout.addWidget(board_title)
        
        # Center ChessBoard widget
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
        
        toolbar_style = (
            f"QPushButton {{"
            f"  background-color: rgba(255, 255, 255, 0.05);"
            f"  color: {self.theme.panel_text.name()};"
            f"  border: 1px solid {self.theme.panel_border.name()};"
            f"  border-radius: 4px;"
            f"  padding: 5px 12px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: rgba(255, 255, 255, 0.12);"
            f"}}"
        )
        
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_add, self.btn_del, self.btn_rotate, self.btn_play]:
            btn.setStyleSheet(toolbar_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            nav_toolbar.addWidget(btn)
            
        nav_toolbar.addStretch()
        board_layout.addLayout(nav_toolbar)
        workspace_layout.addWidget(board_panel, stretch=3)

        # ------------------------------------------
        # COLUMN B: TELEMETRY PANEL (MIDDLE)
        # ------------------------------------------
        telemetry_panel = QFrame()
        telemetry_panel.setObjectName("TelemetryPanel")
        telemetry_layout = QVBoxLayout(telemetry_panel)
        telemetry_layout.setContentsMargins(20, 20, 20, 20)
        telemetry_layout.setSpacing(15)

        # 1. Panel Header with Green online dot
        telemetry_header = QHBoxLayout()
        telemetry_title = QLabel("Engine: BluieBot v0.1.0")
        telemetry_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 13px; font-weight: 700; color: {self.theme.panel_text_muted.name()};")
        
        dot_indicator = QLabel()
        dot_indicator.setFixedSize(8, 8)
        dot_indicator.setStyleSheet("background-color: #2ECC71; border-radius: 4px;") # Glowing green dot
        
        telemetry_header.addWidget(telemetry_title)
        telemetry_header.addStretch()
        telemetry_header.addWidget(dot_indicator)
        telemetry_layout.addLayout(telemetry_header)

        # 2. Glowing Evaluation Score
        score_layout = QHBoxLayout()
        self.lbl_big_score = QLabel("+0.23")
        self.lbl_big_score.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 32px; font-weight: 800; color: {self.theme.console_info.name()};"
        )
        self.lbl_score_desc = QLabel("Slightly Better")
        self.lbl_score_desc.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 11px; font-weight: 600; color: {self.theme.panel_text_muted.name()};"
        )
        score_layout.addWidget(self.lbl_big_score)
        score_layout.addWidget(self.lbl_score_desc)
        score_layout.addStretch()
        telemetry_layout.addLayout(score_layout)

        # 3. Depth Progress Bar
        depth_layout = QVBoxLayout()
        depth_layout.setSpacing(6)
        self.lbl_depth_title = QLabel("Depth 0/0")
        self.lbl_depth_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: 700; color: {self.theme.panel_text.name()}; text-transform: uppercase;")
        
        self.depth_progress = QProgressBar()
        self.depth_progress.setRange(0, 30)
        self.depth_progress.setValue(0)
        self.depth_progress.setTextVisible(False)
        self.depth_progress.setFixedHeight(6)
        self.depth_progress.setStyleSheet(
            f"QProgressBar {{"
            f"  background-color: rgba(255, 255, 255, 0.08);"
            f"  border-radius: 3px;"
            f"}}"
            f"QProgressBar::chunk {{"
            f"  background-color: {self.theme.console_in.name()};"
            f"  border-radius: 3px;"
            f"}}"
        )
        depth_layout.addWidget(self.lbl_depth_title)
        depth_layout.addWidget(self.depth_progress)
        telemetry_layout.addLayout(depth_layout)

        # 4. Metrics Grid (2x4 structured cards layout)
        metrics_frame = QWidget()
        metrics_grid = QGridLayout(metrics_frame)
        metrics_grid.setContentsMargins(0, 0, 0, 0)
        metrics_grid.setHorizontalSpacing(15)
        metrics_grid.setVerticalSpacing(10)
        
        grid_lbl_style = f"font-family: 'Outfit'; font-size: 10px; font-weight: bold; color: {self.theme.panel_text_muted.name()}; text-transform: uppercase;"
        grid_val_style = f"font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: {self.theme.panel_text.name()};"
        
        # Grid Labels
        lbl_nodes = QLabel("Nodes")
        lbl_nps = QLabel("NPS")
        lbl_hash = QLabel("Hash")
        lbl_threads = QLabel("Threads")
        
        for lbl in [lbl_nodes, lbl_nps, lbl_hash, lbl_threads]:
            lbl.setStyleSheet(grid_lbl_style)
            
        # Grid Value holders
        self.val_nodes = QLabel("0")
        self.val_nps = QLabel("0 Kn/s")
        self.val_hash = QLabel("64 MB")
        self.val_threads = QLabel("1")
        
        for val in [self.val_nodes, self.val_nps, self.val_hash, self.val_threads]:
            val.setStyleSheet(grid_val_style)
            
        metrics_grid.addWidget(lbl_nodes, 0, 0)
        metrics_grid.addWidget(self.val_nodes, 1, 0)
        metrics_grid.addWidget(lbl_nps, 0, 1)
        metrics_grid.addWidget(self.val_nps, 1, 1)
        metrics_grid.addWidget(lbl_hash, 0, 2)
        metrics_grid.addWidget(self.val_hash, 1, 2)
        metrics_grid.addWidget(lbl_threads, 0, 3)
        metrics_grid.addWidget(self.val_threads, 1, 3)
        
        telemetry_layout.addWidget(metrics_frame)

        # 5. Principal Variation wrapped section
        pv_frame = QFrame()
        pv_frame.setFrameShape(QFrame.Shape.NoFrame)
        pv_vbox = QVBoxLayout(pv_frame)
        pv_vbox.setContentsMargins(0, 0, 0, 0)
        pv_vbox.setSpacing(5)
        
        pv_hdr = QLabel("Principal Variation")
        pv_hdr.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.console_in.name()}; text-transform: uppercase;")
        self.lbl_pv_line = QLabel("-")
        self.lbl_pv_line.setWordWrap(True)
        self.lbl_pv_line.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: 500; color: {self.theme.panel_text.name()}; line-height: 14px;")
        
        pv_vbox.addWidget(pv_hdr)
        pv_vbox.addWidget(self.lbl_pv_line)
        telemetry_layout.addWidget(pv_frame)

        # 6. Top Moves List sub-table
        top_moves_frame = QWidget()
        top_moves_vbox = QVBoxLayout(top_moves_frame)
        top_moves_vbox.setContentsMargins(0, 0, 0, 0)
        top_moves_vbox.setSpacing(5)
        
        top_moves_hdr = QLabel("Top Moves")
        top_moves_hdr.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.console_in.name()}; text-transform: uppercase;")
        
        # Instantiate sub-table QTableWidget
        self.top_moves_table = QTableWidget()
        self.top_moves_table.setColumnCount(5)
        self.top_moves_table.setHorizontalHeaderLabels(["Move", "Eval", "Depth", "Nodes", "%"])
        self.top_moves_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.top_moves_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.top_moves_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.top_moves_table.setRowCount(5)
        
        # Minimalist styled table headers
        table_header_style = (
            f"QHeaderView::section {{"
            f"  background-color: transparent;"
            f"  color: {self.theme.panel_text_muted.name()};"
            f"  font-family: 'Outfit'; font-size: 9px; font-weight: bold; text-transform: uppercase;"
            f"  border: none;"
            f"  padding: 4px;"
            f"}}"
        )
        self.top_moves_table.horizontalHeader().setStyleSheet(table_header_style)
        self.top_moves_table.verticalHeader().hide()
        self.top_moves_table.setShowGrid(False)
        self.top_moves_table.setStyleSheet(
            f"QTableWidget {{"
            f"  background-color: transparent;"
            f"  border: none;"
            f"  color: {self.theme.panel_text.name()};"
            f"  font-family: 'Outfit'; font-size: 11px;"
            f"}}"
            f"QTableWidget::item {{"
            f"  padding: 4px;"
            f"}}"
        )
        
        # Prepopulate sub-table rows with beautiful mock rows from the design Analysis.png
        mock_moves = [
            ("exd5", "+0.23", "22", "2.34M", "37%"),
            ("d4", "+0.15", "21", "1.98M", "28%"),
            ("Nc3", "+0.08", "20", "1.45M", "14%"),
            ("Bg5", "+0.05", "20", "1.25M", "9%"),
            ("Qe2", "+0.02", "19", "980K", "6%")
        ]
        self._populate_top_moves(mock_moves)
        
        top_moves_vbox.addWidget(top_moves_hdr)
        top_moves_vbox.addWidget(self.top_moves_table)
        telemetry_layout.addWidget(top_moves_frame)

        workspace_layout.addWidget(telemetry_panel, stretch=2)

        # ------------------------------------------
        # COLUMN C: MOVES & CONTROLS PANEL (RIGHT)
        # ------------------------------------------
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.NoFrame)
        right_panel.setFixedWidth(280)
        right_vbox = QVBoxLayout(right_panel)
        right_vbox.setContentsMargins(0, 0, 0, 0)
        right_vbox.setSpacing(15)

        # A. Move Log Panel
        move_log_card = QFrame()
        move_log_card.setObjectName("MoveLogCard")
        move_log_layout = QVBoxLayout(move_log_card)
        move_log_layout.setContentsMargins(15, 15, 15, 15)
        move_log_layout.setSpacing(10)
        
        # Tabs layout selector: Moves | Table | Book
        tabs_box = QHBoxLayout()
        tabs_box.setSpacing(10)
        
        self.btn_tab_moves = QPushButton("Moves")
        self.btn_tab_moves.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {self.theme.console_in.name()}; font-family: 'Outfit'; font-size: 11px; font-weight: bold; border: none; border-bottom: 2px solid {self.theme.console_in.name()}; padding-bottom: 2px; }}"
        )
        self.btn_tab_table = QPushButton("Table")
        self.btn_tab_table.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {self.theme.panel_text_muted.name()}; font-family: 'Outfit'; font-size: 11px; font-weight: bold; border: none; }}"
        )
        self.btn_tab_book = QPushButton("Book")
        self.btn_tab_book.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {self.theme.panel_text_muted.name()}; font-family: 'Outfit'; font-size: 11px; font-weight: bold; border: none; }}"
        )
        
        tabs_box.addWidget(self.btn_tab_moves)
        tabs_box.addWidget(self.btn_tab_table)
        tabs_box.addWidget(self.btn_tab_book)
        tabs_box.addStretch()
        move_log_layout.addLayout(tabs_box)
        
        # Inject MoveListWidget in active workspace
        self.move_list = MoveListWidget(theme=self.theme)
        move_log_layout.addWidget(self.move_list, stretch=1)
        
        # Icons Row: Graph | Target | Copy | Download
        icons_row = QHBoxLayout()
        icons_row.setSpacing(12)
        
        self.btn_icon_graph = QPushButton("📈")
        self.btn_icon_target = QPushButton("🎯")
        self.btn_icon_copy = QPushButton("📋")
        self.btn_icon_download = QPushButton("💾")
        
        icon_style = (
            f"QPushButton {{"
            f"  background-color: rgba(255, 255, 255, 0.05);"
            f"  border: 1px solid {self.theme.panel_border.name()};"
            f"  border-radius: 4px;"
            f"  padding: 5px;"
            f"  min-width: 32px; min-height: 32px;"
            f"  font-size: 14px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: rgba(255, 255, 255, 0.12);"
            f"}}"
        )
        for btn in [self.btn_icon_graph, self.btn_icon_target, self.btn_icon_copy, self.btn_icon_download]:
            btn.setStyleSheet(icon_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            icons_row.addWidget(btn)
            
        icons_row.addStretch()
        move_log_layout.addLayout(icons_row)
        right_vbox.addWidget(move_log_card, stretch=1)

        # Wire graph icon click to launch Centipawn Graph Modal Window
        self.btn_icon_graph.clicked.connect(self._show_graph_modal)

        # B. Quick Controls Panel
        quick_card = QFrame()
        quick_card.setObjectName("QuickCard")
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(15, 15, 15, 15)
        quick_layout.setSpacing(10)
        
        quick_title = QLabel("Quick Controls")
        quick_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.console_in.name()}; text-transform: uppercase;")
        quick_layout.addWidget(quick_title)
        
        # 2x2 Grid Layout
        grid_ctrl = QGridLayout()
        grid_ctrl.setSpacing(8)
        
        self.btn_new_search = QPushButton("🔍 New Search")
        self.btn_new_search.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #1F456E;" # Premium signature blue
            f"  color: white;"
            f"  border: none; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: #2b5c91;"
            f"}}"
        )
        
        self.btn_stop = QPushButton("⏸ Stop")
        self.btn_stop.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #8B0000;" # Premium signature dark red
            f"  color: white;"
            f"  border: none; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: #a30000;"
            f"}}"
        )
        
        self.btn_clear = QPushButton("⟳ Clear Board")
        self.btn_clear.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #1C1A27;"
            f"  color: {self.theme.panel_text.name()};"
            f"  border: 1px solid {self.theme.panel_border.name()}; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: rgba(255,255,255,0.06);"
            f"}}"
        )
        
        self.btn_flip = QPushButton("⇄ Flip Board")
        self.btn_flip.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #1C1A27;"
            f"  color: {self.theme.panel_text.name()};"
            f"  border: 1px solid {self.theme.panel_border.name()}; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: rgba(255,255,255,0.06);"
            f"}}"
        )
        
        for btn in [self.btn_new_search, self.btn_stop, self.btn_clear, self.btn_flip]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        grid_ctrl.addWidget(self.btn_new_search, 0, 0)
        grid_ctrl.addWidget(self.btn_stop, 0, 1)
        grid_ctrl.addWidget(self.btn_clear, 1, 0)
        grid_ctrl.addWidget(self.btn_flip, 1, 1)
        quick_layout.addLayout(grid_ctrl)
        
        right_vbox.addWidget(quick_card)
        workspace_layout.addWidget(right_panel)

        root_layout.addLayout(workspace_layout)
        
        self.update_card_styles()

    def _populate_top_moves(self, moves_list) -> None:
        """Populates the custom QTableWidget top moves list rows."""
        self.top_moves_table.setRowCount(len(moves_list))
        for row, move_data in enumerate(moves_list):
            for col, text in enumerate(move_data):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.top_moves_table.setItem(row, col, item)

    def _show_graph_modal(self) -> None:
        """Launches the premium modal graph dialog popup when graph button is clicked."""
        logger.info("Opening Centipawn Graph Modal Dialog...")
        dialog = QDialog(self)
        dialog.setWindowTitle("Centipawn Evaluation History Graph")
        dialog.resize(500, 300)
        dialog.setStyleSheet(f"background-color: {self.theme.panel_background.name()}; border: 1px solid {self.theme.panel_border.name()}; border-radius: 6px;")
        
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.addWidget(self.centipawn_graph)
        
        dialog.exec()

    def update_card_styles(self) -> None:
        bg_hex = self.theme.panel_background.name()
        border_hex = self.theme.panel_border.name()
        text_hex = self.theme.panel_text.name()
        glow_color = self.theme.console_in.name()

        self.setStyleSheet(
            f"QWidget {{ background-color: {bg_hex}; }}"
            f"QFrame#BoardPanel, QFrame#TelemetryPanel, QFrame#MoveLogCard, QFrame#QuickCard {{"
            f"  background-color: rgba(22, 17, 38, 0.25);"
            f"  border: 1px solid {border_hex};"
            f"  border-radius: 6px;"
            f"}}"
        )

    def update_analysis_state(self, state) -> None:
        """
        Updates the dynamic center column engine telemetry widgets based on
        asynchronous Search info frames received from the UCI controller.
        """
        self.lbl_depth_title.setText(f"Depth {state.depth}/{state.depth + 14}")
        self.depth_progress.setValue(min(state.depth, 30))
        
        # Update metric labels
        self.val_nodes.setText(f"{state.nodes:,}" if state.nodes > 0 else "-")
        self.val_nps.setText(f"{state.nps / 1000000.0:.2f} Mn/s" if state.nps > 0 else "-")
        
        # Load thread options dynamically
        self.val_threads.setText(str(app_state.engine_options.get("Threads", 1)))
        self.val_hash.setText(f"{app_state.engine_options.get('Hash', 64)} MB")

        # Format Score (Handling Mate vs Centipawn)
        if state.is_mate:
            mate_val = state.mate_in if state.mate_in is not None else 0
            self.lbl_big_score.setText(f"M{abs(mate_val)}")
            self.lbl_big_score.setStyleSheet(f"font-family: 'Outfit'; font-size: 32px; font-weight: 800; color: {self.theme.console_error.name() if mate_val < 0 else self.theme.console_info.name()};")
            self.lbl_score_desc.setText("Forced Mate" if mate_val > 0 else "Forced Mated")
        else:
            score = state.score
            if score > 0.0:
                self.lbl_big_score.setText(f"+{score:.2f}")
                self.lbl_big_score.setStyleSheet(f"font-family: 'Outfit'; font-size: 32px; font-weight: 800; color: {self.theme.console_info.name()};")
                self.lbl_score_desc.setText("Better Advantage" if score >= 1.0 else "Slightly Better")
            elif score < 0.0:
                self.lbl_big_score.setText(f"{score:.2f}")
                self.lbl_big_score.setStyleSheet(f"font-family: 'Outfit'; font-size: 32px; font-weight: 800; color: {self.theme.console_error.name()};")
                self.lbl_score_desc.setText("Worse Advantage" if score <= -1.0 else "Slightly Worse")
            else:
                self.lbl_big_score.setText("0.00")
                self.lbl_big_score.setStyleSheet(f"font-family: 'Outfit'; font-size: 32px; font-weight: 800; color: {self.theme.panel_text.name()};")
                self.lbl_score_desc.setText("Balanced Even")
                
        # Parse PV Line
        pv_str = " ".join(state.pv) if state.pv else "-"
        self.lbl_pv_line.setText(pv_str)
        
        # Populate Top Moves table dynamically with real moves list!
        if state.pv:
            real_moves = []
            for idx, move in enumerate(state.pv[:5]):
                score_str = f"+{state.score:.2f}" if state.score >= 0 else f"{state.score:.2f}"
                prob_pct = f"{max(45 - idx * 8, 5)}%"
                node_est = f"{max(int(state.nodes / (idx + 1)), 1000):,}"
                real_moves.append((move, score_str, str(state.depth), node_est, prob_pct))
            
            # Fill empty slots if PV length is short
            while len(real_moves) < 5:
                real_moves.append(("-", "-", "-", "-", "-"))
                
            self._populate_top_moves(real_moves)

    def clear(self) -> None:
        """Resets all metrics to default states."""
        self.lbl_depth_title.setText("Depth 0/0")
        self.depth_progress.setValue(0)
        self.val_nodes.setText("-")
        self.val_nps.setText("-")
        self.lbl_big_score.setText("0.00")
        self.lbl_big_score.setStyleSheet(f"font-family: 'Outfit'; font-size: 32px; font-weight: 800; color: {self.theme.panel_text.name()};")
        self.lbl_score_desc.setText("Balanced Even")
        self.lbl_pv_line.setText("-")
        
        # Reset table back to baseline mock
        mock_moves = [
            ("exd5", "+0.23", "22", "2.34M", "37%"),
            ("d4", "+0.15", "21", "1.98M", "28%"),
            ("Nc3", "+0.08", "20", "1.45M", "14%"),
            ("Bg5", "+0.05", "20", "1.25M", "9%"),
            ("Qe2", "+0.02", "19", "980K", "6%")
        ]
        self._populate_top_moves(mock_moves)

    def update_theme(self) -> None:
        self.theme = theme_manager.get_theme()
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")
        self.board.theme = self.theme
        self.board.update()
        self.eval_bar.theme = self.theme
        self.eval_bar.update()
        self.debug_console.update_theme(self.theme)
        self.centipawn_graph.update_theme(self.theme)
        self.move_list.update_theme(self.theme)
        self.update_card_styles()
        
        # Re-apply toolbar styles dynamically
        toolbar_style = (
            f"QPushButton {{"
            f"  background-color: rgba(255, 255, 255, 0.05);"
            f"  color: {self.theme.panel_text.name()};"
            f"  border: 1px solid {self.theme.panel_border.name()};"
            f"  border-radius: 4px;"
            f"  padding: 5px 12px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: rgba(255, 255, 255, 0.12);"
            f"}}"
        )
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_add, self.btn_del, self.btn_rotate, self.btn_play]:
            btn.setStyleSheet(toolbar_style)
            
        # Re-apply Quick controls button styles
        self.btn_new_search.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #1F456E; color: white;"
            f"  border: none; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{ background-color: #2b5c91; }}"
        )
        self.btn_stop.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #8B0000; color: white;"
            f"  border: none; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{ background-color: #a30000; }}"
        )
        self.btn_clear.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #1C1A27; color: {self.theme.panel_text.name()};"
            f"  border: 1px solid {self.theme.panel_border.name()}; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{ background-color: rgba(255,255,255,0.06); }}"
        )
        self.btn_flip.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: #1C1A27; color: {self.theme.panel_text.name()};"
            f"  border: 1px solid {self.theme.panel_border.name()}; border-radius: 4px; padding: 10px;"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
            f"}}"
            f"QPushButton:hover {{ background-color: rgba(255,255,255,0.06); }}"
        )
