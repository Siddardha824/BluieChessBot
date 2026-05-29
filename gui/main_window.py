# gui/main_window.py

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QTimer

from gui.controllers.game_controller import GameController
from gui.widgets.nav_sidebar import NavSidebar
from gui.views.dashboard_view import DashboardView
from gui.views.analysis_view import AnalysisView
from gui.views.training_view import TrainingView
from gui.views.testing_view import TestingView
from gui.views.benchmark_view import BenchmarkView
from gui.views.tools_view import ToolsView
from gui.views.settings_view import SettingsView
from gui.core.app_state import app_state
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
        self.analysis_view.debug_console.log_message("INFO", "Bluie Chess GUI system successfully bootstrapped.")
        self.analysis_view.debug_console.log_message("INFO", "Awaiting user moves on the chessboard...")

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
        # The dynamic three-column analysis workspace is fully encapsulated inside AnalysisView
        self.dashboard_view = DashboardView()
        self.analysis_view = AnalysisView(engine_manager=self.game_controller.engine_manager)
        self.training_view = TrainingView()
        self.testing_view = TestingView(engine_manager=self.game_controller.engine_manager)
        self.benchmark_view = BenchmarkView(engine_manager=self.game_controller.engine_manager)
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

        # Inject Board Models directly into ChessBoard inside AnalysisView
        self.analysis_view.board.set_models(
            self.game_controller.board_state,
            self.game_controller.highlight_manager
        )

        # E. Assemble root layout (HBoxLayout: Left Sidebar | Central QStackedWidget)
        root_widget = QWidget()
        theme = self.analysis_view.theme
        root_widget.setStyleSheet(f"background-color: {theme.panel_background.name()};")
        
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

        # Wire two-way reactive page synchronization
        app_state.signals.page_changed.connect(self._sync_active_page)

        # Wire reactive dynamic theme swapper repaints
        app_state.signals.theme_changed.connect(self._handle_theme_changed)

        # Connect clicking event from BoardWidget to Controller slot using safe lambda
        self.analysis_view.board.square_clicked.connect(lambda idx: self.game_controller.handle_square_clicked(idx))
        
        # Connect state changes from Controller to trigger BoardWidget repaints
        self.game_controller.signals.state_changed.connect(lambda: self.analysis_view.board.update())
        
        # Wire Phase 2 move histories
        self.game_controller.signals.move_executed.connect(lambda san: self.analysis_view.move_list.add_move(san))
        self.game_controller.signals.move_executed.connect(
            lambda san: self.analysis_view.centipawn_graph.add_score(self.analysis_view.eval_bar.evaluation)
        )
        
        # Stream user move events in console log
        self.game_controller.signals.move_executed.connect(
            lambda san: self.analysis_view.debug_console.log_message("INFO", f"Move registered: {san}")
        )
        
        # Stream game over outcomes (checkmates, stalemates, draws) in console log
        self.game_controller.signals.game_over.connect(
            lambda outcome: self.analysis_view.debug_console.log_message("INFO", f"🏆 GAME OVER: {outcome}")
        )
        
        # Wire Phase 3 move undone connection
        self.game_controller.signals.move_undone.connect(lambda: self.analysis_view.move_list.remove_last_move())
        self.game_controller.signals.move_undone.connect(
            lambda: self.analysis_view.centipawn_graph.history.pop() if len(self.analysis_view.centipawn_graph.history) > 1 else None
        )
        self.game_controller.signals.move_undone.connect(
            lambda: self.analysis_view.centipawn_graph.update()
        )
        
        # Wire Engine Signals directly to sub-panels
        engine_mgr = self.game_controller.engine_manager
        
        # 1. Connect stdout/stdin logs directly to console (direction "IN" -> "UCI_IN")
        engine_mgr.uci_io_logged.connect(
            lambda text, direction: self.analysis_view.debug_console.log_message(f"UCI_{direction}", text)
        )
        
        # 2. Connect engine metric info data blocks to the custom middle column
        engine_mgr.info_received.connect(lambda state: self.analysis_view.update_analysis_state(state))
        engine_mgr.info_received.connect(
            lambda state: self.analysis_view.eval_bar.set_evaluation(state.score, state.is_mate, state.mate_in)
        )
        engine_mgr.info_received.connect(
            lambda state: self.analysis_view.centipawn_graph.update_score(state.score)
        )
        
        # 3. Connect engine process alerts and state status descriptions
        engine_mgr.status_changed.connect(
            lambda status: self.analysis_view.debug_console.log_message("INFO", f"Engine status changed: {status}")
        )
        engine_mgr.engine_error.connect(
            lambda err: self.analysis_view.debug_console.log_message("ERROR", f"Engine error: {err}")
        )
        engine_mgr.bestmove_received.connect(
            lambda move: self.analysis_view.debug_console.log_message("INFO", f"Engine chose move: {move}")
        )

        # Wire Toolbar Navigation buttons
        self.analysis_view.btn_first.clicked.connect(lambda: self._handle_nav_first())
        self.analysis_view.btn_prev.clicked.connect(lambda: self.game_controller.undo_last_move())
        self.analysis_view.btn_next.clicked.connect(lambda: self.game_controller.trigger_engine_move())
        self.analysis_view.btn_last.clicked.connect(lambda: self.game_controller.trigger_engine_move())
        self.analysis_view.btn_rotate.clicked.connect(lambda: self.analysis_view.board.update())
        
        # Wire Quick Controls buttons
        self.analysis_view.btn_new_search.clicked.connect(lambda: self.game_controller.trigger_engine_move())
        self.analysis_view.btn_stop.clicked.connect(lambda: self.game_controller.engine_manager.stop_search())
        
        # Clear Board sets starting FEN position and clears move lists
        self.analysis_view.btn_clear.clicked.connect(lambda: self._handle_clear_board())
        self.analysis_view.btn_flip.clicked.connect(lambda: self._handle_flip_board())

    def _handle_nav_first(self) -> None:
        """Navigates back to the starting position."""
        while len(self.game_controller.board_state._board.move_stack) > 0:
            self.game_controller.undo_last_move()
        self.analysis_view.debug_console.log_message("INFO", "Reset to starting position.")

    def _handle_clear_board(self) -> None:
        """Clears all moves and resets the board to the default starting FEN."""
        self.game_controller.engine_manager.send_command("ucinewgame")
        self.game_controller.board_state.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.analysis_view.move_list.clear()
        self.analysis_view.clear()
        self.analysis_view.board.update()
        self.game_controller.sync_position_and_query_legals()
        self.analysis_view.debug_console.log_message("INFO", "Chessboard cleared and reset.")

    def _handle_flip_board(self) -> None:
        """Logs a mock flip view toggle in the telemetry console logs."""
        self.analysis_view.debug_console.log_message("INFO", "Board perspective flipped.")

    def _handle_page_switch(self, page_key: str) -> None:
        """Transitions active page state in the global AppState model."""
        app_state.active_page = page_key

    def _sync_active_page(self, page_key: str) -> None:
        """Keeps navigation sidebar and stacked widget indices in perfect sync reactively."""
        self.nav_sidebar.set_active_page(page_key)
        
        # When moving to Dashboard, refresh lifetime telemetry stats dynamically
        if page_key == "DASHBOARD":
            self.dashboard_view.refresh_stats()

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
        logger.info(f"MainWindow dynamically synced active view to: {page_key}")

    def _handle_theme_changed(self, theme_name: str) -> None:
        """Propagates active theme repaint styles recursively across all views on-the-fly."""
        from gui.themes.theme_manager import theme_manager
        active_theme = theme_manager.get_theme()
        
        # Trigger updates on stacked views
        self.dashboard_view.update_theme()
        self.analysis_view.update_theme()
        self.training_view.update_theme()
        self.testing_view.update_theme()
        self.benchmark_view.update_theme()
        self.tools_view.update_theme()
        self.settings_view.update_theme()
        self.nav_sidebar.update_theme()
        
        # Apply custom root background updates
        self.centralWidget().setStyleSheet(f"background-color: {active_theme.panel_background.name()};")
        logger.info(f"MainWindow dynamic repaint of active themes finished: {theme_name}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Safely halts search computations and terminates subprocesses before closure.
        """
        logger.info("MainWindow closeEvent received. Releasing resources...")
        self.game_controller.cleanup()
        event.accept()
