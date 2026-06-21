from PySide6.QtWidgets import (
    QHBoxLayout
)

from gui.app.ui.templates import StyledWidget
from gui.utils import get_logger

logger = get_logger(__name__)

class PlayersPanel(StyledWidget):
    """
    A Panel that shows the currently playing players, the time for both sides, Captured Pieces
    """
    def __init__(self, app_manager, parent = None):
        super().__init__("playersPanel", parent)
        self._manager = app_manager
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 8, 6, 8)
        main_layout.setSpacing(6)

        

