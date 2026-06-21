from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QScrollArea, QFrame

from ..templates import StyledWidget
from ..panels import Chessboard, ControlPanel, EvaluationPanel, MoveHistoryPanel, PlayersPanel

class HomePage(StyledWidget):
    def __init__(self, app_manager, parent = None):
        super().__init__("homePage", parent)

        self.manager = app_manager
        self._sizes_initialized = False
        self._resize_timer = None

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        self.board = Chessboard(self.manager, self)
        
        self.control_panel = ControlPanel(self.manager, self)
        self.evaluation_panel = EvaluationPanel(self.manager, self)
        self.move_history = MoveHistoryPanel(self.manager, self)
        self.players_panel = PlayersPanel(self.manager, self)
        
        # Wrap Move History Panel in QScrollArea
        self.scroll_history = QScrollArea(self)
        self.scroll_history.setObjectName("scrollHistory")
        self.scroll_history.setWidgetResizable(True)
        self.scroll_history.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_history.setWidget(self.move_history)
        self.scroll_history.setMinimumWidth(150)
        self.scroll_history.setMaximumWidth(280)
        self.scroll_history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Wrap Players Panel in QScrollArea
        self.scroll_players = QScrollArea(self)
        self.scroll_players.setObjectName("scrollPlayers")
        self.scroll_players.setWidgetResizable(True)
        self.scroll_players.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_players.setWidget(self.players_panel)
        self.scroll_players.setMinimumHeight(150)
        
        # Wrap Control Panel in QScrollArea
        self.scroll_control = QScrollArea(self)
        self.scroll_control.setObjectName("scrollControl")
        self.scroll_control.setWidgetResizable(True)
        self.scroll_control.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_control.setWidget(self.control_panel)
        self.scroll_control.setMinimumHeight(150)
        
        # Wrap Evaluation Panel in QScrollArea
        self.scroll_eval = QScrollArea(self)
        self.scroll_eval.setObjectName("scrollEval")
        self.scroll_eval.setWidgetResizable(True)
        self.scroll_eval.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_eval.setWidget(self.evaluation_panel)
        self.scroll_eval.setMinimumHeight(100)
        
        # Create Vertical Splitter for the left sidebar
        self.left_sidebar_splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.left_sidebar_splitter.setObjectName("leftSidebarSplitter")
        self.left_sidebar_splitter.setHandleWidth(3)
        self.left_sidebar_splitter.addWidget(self.scroll_control)
        self.left_sidebar_splitter.addWidget(self.scroll_eval)
        self.left_sidebar_splitter.setSizes([350, 250])

        # Create Vertical Splitter for the right sidebar
        self.right_sidebar_splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.right_sidebar_splitter.setObjectName("rightSidebarSplitter")
        self.right_sidebar_splitter.setHandleWidth(3)
        self.right_sidebar_splitter.addWidget(self.scroll_history)
        self.right_sidebar_splitter.addWidget(self.scroll_players)
        self.right_sidebar_splitter.setSizes([400, 200])
        
        # Create Horizontal Splitter containing Sidebar, Chessboard, and Move History
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.main_splitter.setObjectName("mainSplitter")
        self.main_splitter.setHandleWidth(3)
        self.main_splitter.addWidget(self.left_sidebar_splitter)
        self.main_splitter.addWidget(self.board)
        self.main_splitter.addWidget(self.right_sidebar_splitter)
        
        layout.addWidget(self.main_splitter)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if not self._sizes_initialized:
            if self._resize_timer is not None:
                self._resize_timer.stop()
                self._resize_timer.deleteLater()
            
            self._resize_timer = QTimer(self)
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self._on_resize_settled)
            self._resize_timer.start(150)

    def _on_resize_settled(self) -> None:
        if not self._sizes_initialized:
            self.initialize_splitter_sizes()

    def initialize_splitter_sizes(self):
        from gui.utils import get_logger
        logger = get_logger(__name__)
        
        splitter_w = self.main_splitter.width()
        splitter_h = self.main_splitter.height()
        
        if splitter_w <= 10 or splitter_h <= 10:
            logger.info("Splitter size not settled yet: width=%s, height=%s. Delaying initialization.", splitter_w, splitter_h)
            if self._resize_timer is not None:
                self._resize_timer.start(150)
            return
            
        # 2 handles of 3px each
        handles_w = self.main_splitter.handleWidth() * (self.main_splitter.count() - 1)
        total_available_w = splitter_w - handles_w
        
        history_w = self.scroll_history.maximumWidth()
        board_w = splitter_h
        sidebar_w = max(100, total_available_w - history_w - board_w)
        
        logger.info("Initializing splitter sizes on startup (settled): Sidebar=%s, Board=%s, History=%s (Splitter H=%s, W=%s, Available W=%s)", 
                    sidebar_w, board_w, history_w, splitter_h, splitter_w, total_available_w)
        self.main_splitter.setSizes([sidebar_w, board_w, history_w])
        self._sizes_initialized = True

