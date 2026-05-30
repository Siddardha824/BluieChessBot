# gui/views/analysis/sections/control_section.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from gui.views.analysis.styles.analysis_styles import get_control_label_style
from gui.widgets import EngineControlWidget

class ControlSection(QFrame):
    # Public signals to forward events to parent/controller if needed
    new_search_clicked = Signal()
    stop_clicked = Signal()
    clear_board_clicked = Signal()
    flip_board_clicked = Signal()

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
        
        # Section Header
        title_lbl = QLabel("Engine Controls")
        title_lbl.setStyleSheet(get_control_label_style(self.theme))
        layout.addWidget(title_lbl)
        
        # Instantiate the pure atomic EngineControlWidget
        self.control_widget = EngineControlWidget(theme=self.theme)
        layout.addWidget(self.control_widget)
        
        # Forward atomic signals to local public signals for backwards-compatibility or parent listening
        self.control_widget.start_search.connect(lambda params: self.new_search_clicked.emit())
        self.control_widget.stop_search.connect(self.stop_clicked.emit)
        self.control_widget.clear_board.connect(self.clear_board_clicked.emit)
        self.control_widget.flip_board.connect(self.flip_board_clicked.emit)

    def connect_engine(self, engine_manager, game_controller) -> None:
        """
        Wires the atomic EngineControlWidget signals directly to the active engine calculations.
        
        Args:
            engine_manager: Active EngineManager model from controllers.
            game_controller: Active GameController orchestrator.
        """
        self.engine_manager = engine_manager
        self.game_controller = game_controller
        
        # Connect the start search parameter dictionary directly to our engine search broker
        self.control_widget.start_search.connect(self._on_start_search_triggered)
        self.control_widget.stop_search.connect(self._on_stop_search_triggered)

    def _on_start_search_triggered(self, params: dict) -> None:
        """Translates and triggers engine calculations with dynamic search constraints."""
        if not self.engine_manager or not self.game_controller:
            return
            
        # Get active board FEN
        fen = self.game_controller.board_state.get_fen()
        
        # Load FEN into the engine
        self.engine_manager.send_position(fen)
        
        # Retrieve search configurations
        depth = params.get("depth")
        movetime = params.get("movetime")
        nodes = params.get("nodes")
        infinite = params.get("infinite", False)
        
        # Dispatch search command
        self.engine_manager.start_search(
            depth=depth,
            movetime=movetime,
            nodes=nodes,
            infinite=infinite
        )

    def _on_stop_search_triggered(self) -> None:
        """Safely stops any active search thread."""
        if self.engine_manager:
            self.engine_manager.stop_search()

    def update_theme(self, theme) -> None:
        """Repaints section theme-dependent stylesheets."""
        self.theme = theme
        self.control_widget.update_theme(self.theme)
