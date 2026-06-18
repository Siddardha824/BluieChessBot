from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from gui.app.game.models.game_state import GameModes

class PlayModeSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("playModeSelector")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_mode = QLabel("Play Mode:", self)
        self.lbl_mode.setObjectName("playModeLabel")
        
        self.combo_mode = QComboBox(self)
        self.combo_mode.setObjectName("modeSelector")
        self.combo_mode.addItem("Analysis Mode", GameModes.ANALYSIS)
        self.combo_mode.addItem("Player vs Engine (White)", GameModes.PLAY_WHITE)
        self.combo_mode.addItem("Player vs Engine (Black)", GameModes.PLAY_BLACK)
        self.combo_mode.addItem("Engine vs Engine", GameModes.ENGINE_VS_ENGINE)
        
        layout.addWidget(self.lbl_mode)
        layout.addWidget(self.combo_mode, 1)
