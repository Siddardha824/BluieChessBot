from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame
)
from gui.app.ui.templates import StyledWidget
from gui.app.game.models.game_state import GameModes
from gui.utils import get_logger

from .play_mode_selector import PlayModeSelector
from .engine_config_table import EngineConfigTable

logger = get_logger(__name__)

class ControlPanel(StyledWidget):
    def __init__(self, app_manager, parent=None):
        super().__init__("controlPanel", parent)
        self._manager = app_manager
        self._game_manager = self._manager.game
        
        self.setMinimumHeight(350)
        self.setup_ui()
        self._connect_signals()
        self._update_mode_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 1. Panel Header Title
        self.lbl_title = QLabel("⚙ ENGINE & PLAY CONTROLS", self)
        self.lbl_title.setObjectName("panelTitle")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.lbl_title.font()
        font.setBold(True)
        font.setPointSize(12)
        self.lbl_title.setFont(font)
        main_layout.addWidget(self.lbl_title)
        
        # 2. Play Mode Selector Component
        self.mode_selector = PlayModeSelector(self)
        main_layout.addWidget(self.mode_selector)
        
        # Divider Line
        divider1 = QFrame(self)
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        divider1.setObjectName("panelDivider1")
        main_layout.addWidget(divider1)
        
        # 3. Engine Config Table Component (Path, Status, Constraints side-by-side)
        self.engine_table = EngineConfigTable(self._manager, self)
        main_layout.addWidget(self.engine_table)
        
        # Divider Line
        divider2 = QFrame(self)
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        divider2.setObjectName("panelDivider2")
        main_layout.addWidget(divider2)
        
        # 4. Action Buttons Grid
        btn_grid = QGridLayout()
        btn_grid.setSpacing(10)
        
        self.btn_action = QPushButton("▶ Start Game", self)
        self.btn_action.setObjectName("actionButton")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_stop = QPushButton("⏹ Stop", self)
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setEnabled(False)
        
        self.btn_flip = QPushButton("⇄ Flip Board", self)
        self.btn_flip.setObjectName("flipButton")
        self.btn_flip.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_reset = QPushButton("⟳ Reset Board", self)
        self.btn_reset.setObjectName("resetButton")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_grid.addWidget(self.btn_action, 0, 0)
        btn_grid.addWidget(self.btn_stop, 0, 1)
        btn_grid.addWidget(self.btn_flip, 1, 0)
        btn_grid.addWidget(self.btn_reset, 1, 1)
        
        main_layout.addLayout(btn_grid)
        main_layout.addStretch(1)

    def _connect_signals(self):
        # Play mode selector changes
        self.mode_selector.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        
        # Action button connections
        self.btn_action.clicked.connect(self._on_action_clicked)
        self.btn_stop.clicked.connect(self._on_stop_clicked)
        self.btn_flip.clicked.connect(self._on_flip_clicked)
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        
        # Connect to GameManager game_over signal
        self._game_manager.game_over.connect(self._on_game_over)

    def _on_mode_changed(self, index):
        mode = self.mode_selector.combo_mode.currentData()
        self._game_manager.set_mode(mode)
        self._update_mode_ui()

    def _update_mode_ui(self):
        mode = self.mode_selector.combo_mode.currentData()
        self.engine_table.update_bindings(mode)
        
        # Toggle button text based on mode
        if mode == GameModes.ANALYSIS:
            self.btn_action.setText("▶ Start Analysis")
            self.btn_stop.setText("⏸ Pause")
        elif mode in (GameModes.PLAY_WHITE, GameModes.PLAY_BLACK):
            self.btn_action.setText("▶ Start Game")
            self.btn_stop.setText("🏳 Resign")
        elif mode == GameModes.ENGINE_VS_ENGINE:
            self.btn_action.setText("▶ Start Match")
            self.btn_stop.setText("⏸ Pause")
            
        self.btn_action.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def _on_action_clicked(self):
        self.engine_table.push_ui_to_settings()
        self._game_manager.start_game()
        self.btn_action.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def _on_stop_clicked(self):
        mode = self._game_manager.state.mode
        if mode in (GameModes.PLAY_WHITE, GameModes.PLAY_BLACK):
            if mode == GameModes.PLAY_WHITE:
                result = "0-1"
                reason = "Resigned"
            else:
                result = "1-0"
                reason = "Resigned"
            self._game_manager.state.result = result
            self._game_manager.state.result_reason = reason
            self._game_manager.stop_game()
            self._game_manager.game_over.emit(result, reason)
        else:
            self._game_manager.stop_game()
            self.btn_action.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def _on_flip_clicked(self):
        # Flip board visual perspective. Route to parent HomePage's board if available.
        # Find if parent HomePage has board attribute
        parent_page = self.parent()
        while parent_page is not None:
            if hasattr(parent_page, "board"):
                parent_page.board.flip()
                break
            parent_page = parent_page.parent()
        logger.info("Flip board perspective clicked")

    def _on_reset_clicked(self):
        self._game_manager.stop_game()
        self.btn_action.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self._manager.board.new_game()
        logger.info("Board reset to starting position")

    def _on_game_over(self, result, reason):
        self.btn_action.setEnabled(True)
        self.btn_stop.setEnabled(False)
