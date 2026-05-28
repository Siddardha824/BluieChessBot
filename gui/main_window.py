# gui/main_window.py

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide6.QtGui import QCloseEvent
from gui.board.board_widget import ChessBoard
from gui.controllers.game_controller import GameController
from gui.panels import MoveListWidget, DebugConsoleWidget, EngineInfoWidget, EvalBarWidget
from gui.widgets.nav_sidebar import NavSidebar
from gui.views.dashboard_view import DashboardView
from gui.views.analysis_view import AnalysisView
from gui.views.training_view import TrainingView
from gui.views.testing_view import TestingView
from gui.views.benchmark_view import BenchmarkView
from gui.views.tools_view import ToolsView
from gui.views.settings_view import SettingsView
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the primary MainWindow layout.
        Acts as the central coordination container connecting widgets and controllers.
        """
        super().__init__()

        self.setWindowTitle("Bluie Chess Workbench")
        self.resize(1200, 750)

        # 1. Instantiate the State Controller
        self.game_controller = GameController(self)

        # 2. Setup layouts & inject models
        self.setup_ui()
        
        # 3. Wire Signals and Slots
        self.wire_connections()
        
        # Log bootstrap success in console
        self.debug_console.log_message("INFO", "Bluie Chess GUI system successfully bootstrapped.")
        self.debug_console.log_message("INFO", "Awaiting user moves on the chessboard...")

        logger.info("MainWindow UI framework successfully bootstrapped.")

    def setup_ui(self) -> None:
        """
        Creates layout structures and instantiates view components, 
        injecting the controller's state models directly.
        """
        # A. Create Navigation Sidebar
        self.nav_sidebar = NavSidebar()
        
        # B. Create Stacked Views Widget
        self.stacked_widget = QStackedWidget()
        
        # C. Instantiate Modular Tab Views
        self.dashboard_view = DashboardView()
        self.analysis_view = AnalysisView()
        self.training_view = TrainingView()
        self.testing_view = TestingView()
        self.benchmark_view = BenchmarkView()
        self.tools_view = ToolsView()
        self.settings_view = SettingsView()
        
        # D. Add views to stacked stack
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.analysis_view)
        self.stacked_widget.addWidget(self.training_view)
        self.stacked_widget.addWidget(self.testing_view)
        self.stacked_widget.addWidget(self.benchmark_view)
        self.stacked_widget.addWidget(self.tools_view)
        self.stacked_widget.addWidget(self.settings_view)

        # E. Create a container widget that encapsulates our entire legacy chess analysis workspace
        analysis_content = QWidget()
        analysis_layout = QVBoxLayout(analysis_content)
        analysis_layout.setContentsMargins(10, 10, 10, 10)
        analysis_layout.setSpacing(10)
        
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)
        
        # Instantiate ChessBoard
        self.board = ChessBoard()
        self.board.set_models(
            self.game_controller.board_state,
            self.game_controller.highlight_manager
        )
        
        # 1. Evaluation Bar (Left of Chessboard)
        self.eval_bar = EvalBarWidget(theme=self.board.theme)
        
        middle_layout.addWidget(self.eval_bar)
        middle_layout.addWidget(self.board)
        
        # 2. Right Sidebar Panel (Move List and Engine Info)
        right_sidebar = QWidget()
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        self.move_list = MoveListWidget(theme=self.board.theme)
        self.engine_info = EngineInfoWidget(theme=self.board.theme)
        
        right_layout.addWidget(self.move_list, stretch=3)
        right_layout.addWidget(self.engine_info, stretch=2)
        
        # Keep sidebar size standard to preserve chessboard central aspect ratio
        right_sidebar.setFixedWidth(280)
        
        middle_layout.addWidget(right_sidebar)
        analysis_layout.addLayout(middle_layout, stretch=4)
        
        # 3. Bottom Debug Console
        self.debug_console = DebugConsoleWidget(
            theme=self.board.theme,
            engine_manager=self.game_controller.engine_manager
        )
        self.debug_console.setFixedHeight(180)
        
        analysis_layout.addWidget(self.debug_console, stretch=1)
        
        # Inject the actual chess workspace inside the modular AnalysisView
        # Removes the placeholder notice widget
        if self.analysis_view.main_layout.count() > 0:
            placeholder = self.analysis_view.main_layout.itemAt(0).widget()
            if placeholder:
                placeholder.setParent(None)
        self.analysis_view.main_layout.addWidget(analysis_content)

        # F. Assemble root layout (HBoxLayout: Left Sidebar | Central QStackedWidget)
        root_widget = QWidget()
        root_widget.setStyleSheet("background-color: #0B0813;")  # Custom cosmic background
        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        root_layout.addWidget(self.nav_sidebar)
        root_layout.addWidget(self.stacked_widget)
        
        self.setCentralWidget(root_widget)

    def wire_connections(self) -> None:
        """
        Locks in uni-directional events using Qt Signals & Slots.
        """
        # Wire navigation sidebar tab clicks
        self.nav_sidebar.page_selected.connect(lambda page_key: self._handle_page_switch(page_key))

        # Connect clicking event from BoardWidget to Controller slot using safe lambda
        self.board.square_clicked.connect(lambda idx: self.game_controller.handle_square_clicked(idx))
        
        # Connect state changes from Controller to trigger BoardWidget repaints
        self.game_controller.signals.state_changed.connect(lambda: self.board.update())
        
        # Wire Phase 2 move histories
        self.game_controller.signals.move_executed.connect(lambda san: self.move_list.add_move(san))
        
        # Stream user move events in console log
        self.game_controller.signals.move_executed.connect(
            lambda san: self.debug_console.log_message("INFO", f"Move registered: {san}")
        )
        
        # Wire Phase 3 move undone connection
        self.game_controller.signals.move_undone.connect(lambda: self.move_list.remove_last_move())
        
        # Wire Engine Signals directly to sub-panels
        engine_mgr = self.game_controller.engine_manager
        
        # 1. Connect stdout/stdin logs directly to console (direction "IN" -> "UCI_IN")
        engine_mgr.uci_io_logged.connect(
            lambda text, direction: self.debug_console.log_message(f"UCI_{direction}", text)
        )
        
        # 2. Connect engine metric info data blocks
        engine_mgr.info_received.connect(lambda state: self.engine_info.update_analysis_state(state))
        engine_mgr.info_received.connect(
            lambda state: self.eval_bar.set_evaluation(state.score, state.is_mate, state.mate_in)
        )
        
        # 3. Connect engine process alerts and state status descriptions
        engine_mgr.status_changed.connect(
            lambda status: self.debug_console.log_message("INFO", f"Engine status changed: {status}")
        )
        engine_mgr.engine_error.connect(
            lambda err: self.debug_console.log_message("ERROR", f"Engine error: {err}")
        )
        engine_mgr.bestmove_received.connect(
            lambda move: self.debug_console.log_message("INFO", f"Engine chose move: {move}")
        )
        
        # Wire Debug Overlay dropdown changes from right panel to GameController
        self.engine_info.overlay_mode_changed.connect(
            lambda mode: self.game_controller.set_debug_overlay_mode(mode)
        )

    def _handle_page_switch(self, page_key: str) -> None:
        """Transitions between views inside the stacked widgets stack."""
        from gui.core.app_state import app_state
        app_state.active_page = page_key
        
        page_indices = {
            "DASHBOARD": 0,
            "ANALYSIS": 1,
            "TRAINING": 2,
            "TESTING": 3,
            "BENCHMARK": 4,
            "TOOLS": 5,
            "SETTINGS": 6
        }
        idx = page_indices.get(page_key, 0)
        self.stacked_widget.setCurrentIndex(idx)
        logger.info(f"MainWindow switched active view tab to: {page_key}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Safely halts search computations and terminates subprocesses before closure.
        """
        logger.info("MainWindow closeEvent received. Releasing resources...")
        self.game_controller.cleanup()
        event.accept()
