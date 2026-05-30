# gui/views/analysis/analysis_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QDialog
from PySide6.QtCore import Qt
from gui.utils.logger import get_logger

from gui.views.analysis.styles.analysis_styles import get_main_view_style
from gui.views.analysis.sections.board_section import BoardSection
from gui.views.analysis.sections.telemetry_section import TelemetrySection
from gui.views.analysis.sections.move_section import MoveSection
from gui.views.analysis.sections.control_section import ControlSection

from gui.panels.eval_bar_widget import EvalBarWidget
from gui.panels.debug_console_widget import DebugConsoleWidget
from gui.panels.centipawn_graph_widget import CentipawnGraphWidget

logger = get_logger(__name__)

class AnalysisView(QWidget):
    def __init__(self, engine_manager=None, parent=None):
        """
        Initializes the consolidated 3-column AnalysisView.
        Constructs a horizontal row layout of modular sections with a full-width
        DebugConsole at the bottom.
        """
        super().__init__(parent)
        from gui.themes import theme_manager
        self.theme = theme_manager.get_theme()
        self.engine_manager = engine_manager
        
        self._init_ui()
        
        # Wire calculations up to telemetry if manager is injected on initialization
        if self.engine_manager is not None:
            self.connect_engine(self.engine_manager, None)

    def _init_ui(self) -> None:
        # Main layout is vertical (Workspace horizontal row + Debug Console bottom row)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 1. Workspace horizontal row container
        workspace_layout = QHBoxLayout()
        workspace_layout.setSpacing(10)
        
        # Column 1: Move log section (Left)
        self.move_section = MoveSection(theme=self.theme)
        workspace_layout.addWidget(self.move_section, stretch=1)
        
        # Column 2: Chessboard area section (Center)
        self.board_section = BoardSection(theme=self.theme)
        workspace_layout.addWidget(self.board_section, stretch=2)
        
        # Column 3: Telemetry & Controls stacked panel (Right)
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.NoFrame)
        right_vbox = QVBoxLayout(right_panel)
        right_vbox.setContentsMargins(0, 0, 0, 0)
        right_vbox.setSpacing(10)
        
        self.telemetry_section = TelemetrySection(theme=self.theme, engine_info=self.engine_manager.engine_info if self.engine_manager else None)
        right_vbox.addWidget(self.telemetry_section, stretch=3)
        
        self.control_section = ControlSection(theme=self.theme)
        right_vbox.addWidget(self.control_section, stretch=2)
        
        workspace_layout.addWidget(right_panel, stretch=1)
        main_layout.addLayout(workspace_layout, stretch=1)
        
        # 2. Bottom Row: Debug Console Widget (Full width)
        self.debug_console = DebugConsoleWidget(theme=self.theme)
        main_layout.addWidget(self.debug_console, stretch=0)
        
        # Apply stylesheet
        self.setStyleSheet(get_main_view_style(self.theme))
        
        # 3. Expose aliases for backwards-compatibility with controller / MainWindow bindings
        self.board = self.board_section.board
        self.move_list = self.move_section.move_list
        self.eval_bar = EvalBarWidget(theme=self.theme)
        self.eval_bar.hide()
        self.centipawn_graph = CentipawnGraphWidget(theme=self.theme)
        
        # Forward button references
        self.btn_new_search = self.control_section.control_widget.btn_new_search
        self.btn_stop = self.control_section.control_widget.btn_stop
        self.btn_clear = self.control_section.control_widget.btn_clear
        self.btn_flip = self.control_section.control_widget.btn_flip
        
        # Wire icons row modal buttons
        self.move_section.btn_icon_graph.clicked.connect(self._show_graph_modal)

    def connect_engine(self, engine_manager, game_controller=None) -> None:
        """
        Dynamic wiring broker to connect UCI engine calculation updates and search controls.
        
        Args:
            engine_manager: Active EngineManager backend model.
            game_controller: Active GameController orchestrator (optional).
        """
        self.engine_manager = engine_manager
        
        # Wire active telemetry updating slots
        self.telemetry_section.engine_info = engine_manager.engine_info
        self.telemetry_section.sync_engine_info()
        
        # Bind reactive updates
        engine_manager.info_received.connect(self.telemetry_section.update_analysis_state)
        
        # Reset telemetry metrics on search start
        def handle_status_change(status: str) -> None:
            if status == "Searching":
                self.telemetry_section.clear()
        engine_manager.status_changed.connect(handle_status_change)
        
        # Connect UCI stream standard logging to bottom DebugConsole
        engine_manager.uci_io_logged.connect(
            lambda text, direction: self.debug_console.log_message(f"UCI_{direction}", text)
        )
        
        # Connect status/alert logs
        engine_manager.status_changed.connect(
            lambda status: self.debug_console.log_message("INFO", f"Engine status changed: {status}")
        )
        engine_manager.engine_error.connect(
            lambda err: self.debug_console.log_message("ERROR", f"Engine error: {err}")
        )
        engine_manager.bestmove_received.connect(
            lambda move: self.debug_console.log_message("INFO", f"Engine chose move: {move}")
        )
        
        # Connect legacy Advantage/Eval and Chart widgets to search updates
        engine_manager.info_received.connect(
            lambda state: self.eval_bar.set_evaluation(state.score, state.is_mate, state.mate_in)
        )
        engine_manager.info_received.connect(
            lambda state: self.centipawn_graph.update_score(state.score)
        )
        
        # Delegate controls integration and board move updates if controller is active
        if game_controller is not None:
            self.control_section.connect_engine(engine_manager, game_controller)
            
            # Connect board move execution events
            game_controller.signals.move_executed.connect(
                lambda san: self.move_list.add_move(san)
            )
            game_controller.signals.move_executed.connect(
                lambda san: self.centipawn_graph.add_score(self.eval_bar.evaluation)
            )
            game_controller.signals.move_executed.connect(
                lambda san: self.debug_console.log_message("INFO", f"Move registered: {san}")
            )
            game_controller.signals.game_over.connect(
                lambda outcome: self.debug_console.log_message("INFO", f"🏆 GAME OVER: {outcome}")
            )
            
            # Connect board move undo events
            game_controller.signals.move_undone.connect(
                lambda: self.move_list.remove_last_move()
            )
            game_controller.signals.move_undone.connect(
                lambda: self.centipawn_graph.history.pop() if len(self.centipawn_graph.history) > 1 else None
            )
            game_controller.signals.move_undone.connect(
                lambda: self.centipawn_graph.update()
            )


    def update_analysis_state(self, state) -> None:
        """Routes dynamic telemetry updates to sub-section."""
        self.telemetry_section.update_analysis_state(state)

    def clear(self) -> None:
        """Resets dynamic metrics grids and advantages scores."""
        self.telemetry_section.clear()

    def _show_graph_modal(self) -> None:
        """Launches the centipawn analysis evaluation history graph modal."""
        logger.info("Opening Centipawn Graph Modal Dialog...")
        dialog = QDialog(self)
        dialog.setWindowTitle("Centipawn Evaluation History Graph")
        dialog.resize(500, 300)
        dialog.setStyleSheet(
            f"background-color: {self.theme.panel_background.name()}; "
            f"border: 1px solid {self.theme.panel_border.name()}; "
            f"border-radius: 6px;"
        )
        
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.addWidget(self.centipawn_graph)
        
        dialog.exec()

    def update_theme(self, theme) -> None:
        """Propagates dynamic color palette shifts recursively to all nested sections."""
        self.theme = theme
        self.setStyleSheet(get_main_view_style(self.theme))
        
        # Recursive updates
        self.board_section.update_theme(self.theme)
        self.telemetry_section.update_theme(self.theme)
        self.move_section.update_theme(self.theme)
        self.control_section.update_theme(self.theme)
        self.debug_console.update_theme(self.theme)
        self.centipawn_graph.update_theme(self.theme)
