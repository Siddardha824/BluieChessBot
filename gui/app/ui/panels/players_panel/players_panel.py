from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy,
    QVBoxLayout,
)

from gui.app.ui.templates import StyledWidget
from gui.app.shared import ICONS_DIR
from gui.utils import get_logger

logger = get_logger(__name__)


class PlayersPanel(StyledWidget):
    """
    Shows player information and position information.
    """

    def __init__(self, app_manager, parent=None):
        super().__init__("playersPanel", parent)

        self._manager = app_manager
        self._theme = self._manager.theme
        
        self._load_icons()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 8, 6, 8)
        main_layout.setSpacing(6)

        # Panel header
        self.lbl_title = QLabel("PLAYERS & POSITION", self)
        self.lbl_title.setObjectName("panelTitle")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = self.lbl_title.font()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.lbl_title.setFont(title_font)
        main_layout.addWidget(self.lbl_title)
        main_layout.addWidget(self._create_separator())

        # =========================
        # White Player
        # =========================

        white_layout = QGridLayout()

        white_layout.addWidget(self._player_icon_white, 0, 0, 2, 2)

        white_header_layout = QHBoxLayout()
        white_header_layout.setContentsMargins(0, 0, 0, 0)
        white_header_layout.setSpacing(6)
        self.white_name_label = QLabel("White", self)
        self.white_name_label.setObjectName("playerNameLabel")

        self.white_material_label = QLabel("", self)
        self.white_material_label.setObjectName("materialLabel")
        self.white_material_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        white_header_layout.addWidget(self.white_name_label)
        white_header_layout.addWidget(self.white_material_label, 1)
        white_layout.addLayout(white_header_layout, 0, 2)

        self.white_captured_label = QLabel("", self)
        self.white_captured_label.setObjectName("capturedPiecesLabel")
        self.white_captured_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        
        white_layout.addWidget(self.white_captured_label, 1, 2)
        main_layout.addLayout(white_layout)
        main_layout.addWidget(self._create_separator())

        # =========================
        # Position Information
        # =========================

        # self.position_title = QLabel("POSITION", self)
        # self.position_title.setObjectName("positionHeader")

        # main_layout.addWidget(self.position_title)

        # self.side_to_move_label = QLabel("Side: White", self)
        # self.side_to_move_label.setObjectName("positionInfoLabel")

        # self.move_number_label = QLabel("Move: 1", self)
        # self.move_number_label.setObjectName("positionInfoLabel")

        # self.castling_label = QLabel("Castling: KQkq", self)
        # self.castling_label.setObjectName("positionInfoLabel")

        # self.status_label = QLabel("Status: Ongoing", self)
        # self.status_label.setObjectName("positionInfoLabel")

        # main_layout.addWidget(self.side_to_move_label)
        # main_layout.addWidget(self.move_number_label)
        # main_layout.addWidget(self.castling_label)
        # main_layout.addWidget(self.status_label)

        # main_layout.addWidget(self._create_separator())

        # =========================
        # Black Player
        # =========================

        black_layout = QGridLayout()

        black_layout.addWidget(self._player_icon_black, 0, 0, 2, 2)

        black_header_layout = QHBoxLayout()
        black_header_layout.setContentsMargins(0, 0, 0, 0)
        black_header_layout.setSpacing(6)

        self.black_name_label = QLabel("Black", self)
        self.black_name_label.setObjectName("playerNameLabel")

        self.black_material_label = QLabel("", self)
        self.black_material_label.setObjectName("materialLabel")
        self.black_material_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        black_header_layout.addWidget(self.black_name_label)
        black_header_layout.addWidget(self.black_material_label, 1)
        black_layout.addLayout(black_header_layout, 0, 2)

        self.black_captured_label = QLabel("", self)
        self.black_captured_label.setObjectName("capturedPiecesLabel")
        self.black_captured_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        black_layout.addWidget(self.black_captured_label, 1, 2)
        main_layout.addLayout(black_layout)
        main_layout.addStretch()

    def _create_separator(self) -> QFrame:
        separator = QFrame(self)
        separator.setObjectName("panelSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator
    
    def _load_icons(self):
        theme = self._theme.active_theme

        player_icon = ICONS_DIR / ("player_" + theme)
        self._player_icon_white = QLabel(self)
        self._player_icon_black = QLabel(self)

        pixmap = QPixmap(player_icon)
        pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self._player_icon_white.setPixmap(pixmap)
        self._player_icon_white.setScaledContents(False)

        self._player_icon_black.setPixmap(pixmap)
        self._player_icon_black.setScaledContents(False)

        



