# gui/views/analysis/sections/diagnostics_section.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox, QTextEdit
from PySide6.QtCore import Qt, Signal
from gui.views.analysis.styles.analysis_styles import (
    get_control_label_style, get_pv_line_style, get_combo_style
)

class DiagnosticsSection(QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.engine_manager = None
        self.game_controller = None
        self.setObjectName("QuickCard")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 1. Section Title
        title_lbl = QLabel("Engine Diagnostics")
        title_lbl.setStyleSheet(get_control_label_style(self.theme))
        layout.addWidget(title_lbl)
        
        # 2. Debug Overlay Control Row
        overlay_box = QHBoxLayout()
        overlay_box.setSpacing(8)
        
        overlay_lbl = QLabel("Debug Overlay:")
        overlay_lbl.setStyleSheet(get_control_label_style(self.theme))
        
        self.combo_overlay = QComboBox()
        self.combo_overlay.addItem("None (Disabled)", "NONE")
        self.combo_overlay.addItem("White Attack Map", "WHITE_ATTACKS")
        self.combo_overlay.addItem("Black Attack Map", "BLACK_ATTACKS")
        self.combo_overlay.addItem("Engine Legal Targets", "ENGINE_LEGALS")
        self.combo_overlay.addItem("Attacks To (White)", "ATTACKSTO_WHITE")
        self.combo_overlay.addItem("Attacks To (Black)", "ATTACKSTO_BLACK")
        self.combo_overlay.setStyleSheet(get_combo_style(self.theme))
        self.combo_overlay.currentIndexChanged.connect(self._on_overlay_changed)
        
        overlay_box.addWidget(overlay_lbl)
        overlay_box.addWidget(self.combo_overlay, stretch=1)
        layout.addLayout(overlay_box)
        
        # Divider Line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet(f"background-color: {self.theme.panel_border.name()}; max-height: 1px; border: none;")
        layout.addWidget(divider)
        
        # 3. Move Generator Inspector
        inspector_title = QLabel("Move Gen Inspector")
        inspector_title.setStyleSheet(get_control_label_style(self.theme))
        layout.addWidget(inspector_title)
        
        self.lbl_selected_square = QLabel("Selected Square: None")
        self.lbl_selected_square.setStyleSheet(get_pv_line_style(self.theme))
        layout.addWidget(self.lbl_selected_square)
        
        self.txt_inspector_moves = QTextEdit()
        self.txt_inspector_moves.setReadOnly(True)
        self.txt_inspector_moves.setPlaceholderText("Select a friendly piece on the board to inspect generated legal moves...")
        self.txt_inspector_moves.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: rgba(0, 0, 0, 0.25);"
            f"  border: 1px solid {self.theme.panel_border.name()};"
            f"  border-radius: 4px;"
            f"  padding: 6px;"
            f"  color: {self.theme.panel_text.name()};"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 500;"
            f"}}"
        )
        layout.addWidget(self.txt_inspector_moves, stretch=1)

    def connect_engine(self, engine_manager, game_controller) -> None:
        """
        Connects diagnostics queries to controllers and board highlights.
        """
        self.engine_manager = engine_manager
        self.game_controller = game_controller
        
        # Listen reactively to square selection changes on the board
        self.game_controller.board_controller.selection_changed.connect(self.sync_move_inspector)
        self.sync_move_inspector()

    def _on_overlay_changed(self, index: int) -> None:
        """Toggles selected debug threat overlay on active game controller."""
        if self.game_controller:
            mode = self.combo_overlay.currentData()
            self.game_controller.set_debug_overlay_mode(mode)

    def sync_move_inspector(self) -> None:
        """
        Filters and displays generated legal moves for the currently selected square.
        """
        if not self.game_controller:
            self.lbl_selected_square.setText("Selected Square: None")
            self.txt_inspector_moves.setText("")
            return
            
        sq_idx = self.game_controller.highlight_manager.selected_square
        if sq_idx is None:
            self.lbl_selected_square.setText("Selected Square: None")
            self.txt_inspector_moves.setPlaceholderText("Select a friendly piece on the board to inspect generated legal moves...")
            self.txt_inspector_moves.setText("")
            return
            
        # 1. Translate index to coordinate (e.g. 12 -> 'e2')
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        col = sq_idx % 8
        row = 8 - (sq_idx // 8)
        sq_coord = f"{files[col]}{row}"
        self.lbl_selected_square.setText(f"Selected Square: {sq_coord}")
        
        # 2. Extract engine legal moves cached in BoardState model
        cached_moves = getattr(self.game_controller.board_state, "cached_engine_legal_moves", [])
        if not cached_moves:
            self.txt_inspector_moves.setText("(No legal moves currently calculated or cached by engine)")
            return
            
        # 3. Filter moves whose starting coordinate matches our selected square
        filtered_moves = [move for move in cached_moves if move.startswith(sq_coord)]
        if filtered_moves:
            # Format nicely as a comma-separated list
            formatted_text = ", ".join(filtered_moves)
            self.txt_inspector_moves.setText(formatted_text)
        else:
            self.txt_inspector_moves.setText("(No legal moves generated for this piece)")

    def update_theme(self, theme) -> None:
        """Repaints component colors on active theme transitions."""
        self.theme = theme
        self.lbl_selected_square.setStyleSheet(get_pv_line_style(self.theme))
        self.combo_overlay.setStyleSheet(get_combo_style(self.theme))
        
        self.txt_inspector_moves.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: rgba(0, 0, 0, 0.25);"
            f"  border: 1px solid {self.theme.panel_border.name()};"
            f"  border-radius: 4px;"
            f"  padding: 6px;"
            f"  color: {self.theme.panel_text.name()};"
            f"  font-family: 'Outfit'; font-size: 11px; font-weight: 500;"
            f"}}"
        )
