from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QScrollArea, QFrame

from ..templates import StyledWidget
from ..panels import Chessboard, ControlPanel, EvaluationPanel

class HomePage(StyledWidget):
    def __init__(self, app_manager, parent = None):
        super().__init__("homePage", parent)

        self.manager = app_manager

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        self.board = Chessboard(self.manager, self)
        
        self.control_panel = ControlPanel(self.manager, self)
        self.evaluation_panel = EvaluationPanel(self.manager, self)
        
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
        
        # Create Vertical Splitter for the sidebar
        self.sidebar_splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.sidebar_splitter.setObjectName("sidebarSplitter")
        self.sidebar_splitter.addWidget(self.scroll_control)
        self.sidebar_splitter.addWidget(self.scroll_eval)
        self.sidebar_splitter.setSizes([350, 250])
        
        # Create Horizontal Splitter between Chessboard and Sidebar
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.main_splitter.setObjectName("mainSplitter")
        self.main_splitter.addWidget(self.board)
        self.main_splitter.addWidget(self.sidebar_splitter)
        
        # Initial size allocation: board gets 75% width, sidebar gets 25% width
        self.main_splitter.setSizes([600, 200])
        
        layout.addWidget(self.main_splitter)

