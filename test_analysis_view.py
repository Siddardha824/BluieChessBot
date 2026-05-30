# test_analysis_view.py

import sys
import random
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QFrame
from PySide6.QtCore import Qt, QObject, Signal, QTimer

# Configure Python path to resolve imports correctly from workspace root
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.themes.theme_manager import theme_manager
from gui.models.engine_info import EngineInfo
from gui.models.board_state import BoardState
from gui.board.highlights import HighlightManager
from gui.views.analysis.analysis_view import AnalysisView

class MockEngineState:
    def __init__(self, depth, nodes, nps, is_mate, mate_in, score, pv):
        self.depth = depth
        self.nodes = nodes
        self.nps = nps
        self.is_mate = is_mate
        self.mate_in = mate_in
        self.score = score
        self.pv = pv

class MockEngineManager(QObject):
    info_received = Signal(object)
    search_started = Signal()
    status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.engine_info = EngineInfo()
        self.engine_info.name = "Bluie Quantum UCI v2.5"
        self.engine_info.hash_size = 128
        self.engine_info.threads = 4
        self.engine_info.connection_status = "Connected"
        self.engine_info.status = "Ready"
        self.engine_status = "Ready"

    def start_search(self, depth=None, movetime=None, nodes=None, infinite=False):
        print(f"[MockEngine] Starting search... depth={depth}, movetime={movetime}, nodes={nodes}, infinite={infinite}")
        self.engine_status = "Searching"
        self.engine_info.status = "Searching"
        self.search_started.emit()
        self.status_changed.emit("Searching")

    def stop_search(self):
        print("[MockEngine] Stopping search.")
        self.engine_status = "Ready"
        self.engine_info.status = "Ready"
        self.status_changed.emit("Ready")

    def send_position(self, fen):
        print(f"[MockEngine] FEN Position loaded: {fen}")

class MockGameController(QObject):
    def __init__(self, engine_manager):
        super().__init__()
        self.engine_manager = engine_manager
        self.board_state = BoardState()
        self.highlight_manager = HighlightManager()

def main():
    """
    Unified bootstrap script to launch, visually inspect, and interact with
    the fully integrated modular AnalysisView workbench.
    """
    print("Initializing integrated test application...")
    app = QApplication(sys.argv)
    
    # Get active theme
    theme = theme_manager.get_theme()
    print(f"Loaded active theme: {theme.name}")
    
    # 1. Setup mock backends
    engine_manager = MockEngineManager()
    game_controller = MockGameController(engine_manager)
    
    # 2. Main Window setup
    window = QWidget()
    window.setWindowTitle("Test AnalysisView Workbench Integration")
    window.resize(1150, 750)
    window.setStyleSheet(f"background-color: {theme.panel_background.name()};")
    
    layout = QVBoxLayout(window)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)
    
    # Title bar
    header_box = QHBoxLayout()
    header = QLabel("Analysis Workbench Sandbox")
    header.setStyleSheet(
        f"font-family: 'Outfit'; font-size: 16px; font-weight: 800; "
        f"color: {theme.console_in.name()};"
    )
    header_box.addWidget(header)
    header_box.addStretch()
    
    # Theme toggles list
    themes_list = list(theme_manager.themes.keys())
    current_theme_idx = [themes_list.index(theme_manager._current_theme_name)]
    
    btn_cycle_theme = QPushButton(f"🎨 Cycle Theme: {theme.name}")
    btn_cycle_theme.setStyleSheet(
        "QPushButton { background-color: #1F456E; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-family: 'Outfit'; font-size: 11px; font-weight: bold; }"
        "QPushButton:hover { background-color: #2b5c91; }"
    )
    header_box.addWidget(btn_cycle_theme)
    layout.addLayout(header_box)
    
    # 3. Instantiate the master AnalysisView
    analysis_view = AnalysisView(engine_manager=engine_manager)
    layout.addWidget(analysis_view, stretch=1)
    
    # Inject models into board
    analysis_view.board.set_models(game_controller.board_state, game_controller.highlight_manager)
    
    # Wire engine wiring broker in ControlSection
    analysis_view.connect_engine(engine_manager, game_controller)
    
    # 4. Search calculation mock data loops
    search_timer = QTimer()
    search_step = [0]
    
    def on_simulation_step():
        step = search_step[0]
        if engine_manager.engine_status != "Searching":
            search_timer.stop()
            return
            
        # Simulate UCI engine calculation iterations
        depth = 1 + step // 3
        nodes = step * 18000 + 4000
        nps = 180000 + random.randint(-15000, 15000)
        
        # Advantage score drift
        score = 0.15 + (step * 0.04) * (-1 if step % 4 == 0 else 1)
        
        # Moves history line
        pvs = [
            ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4"],
            ["e4", "e5", "Nf3", "Nf6", "Nxe5", "d6", "Nf3"],
            ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5"]
        ]
        active_pv = pvs[step % len(pvs)]
        
        state = MockEngineState(
            depth=depth,
            nodes=nodes,
            nps=nps,
            is_mate=False,
            mate_in=0,
            score=score,
            pv=active_pv
        )
        
        # Trigger updates
        engine_manager.info_received.emit(state)
        analysis_view.debug_console.log_message(
            "UCI_IN", 
            f"info depth {depth} seldepth {depth+2} score cp {int(score*100)} nodes {nodes} nps {nps} pv {' '.join(active_pv)}"
        )
        search_step[0] += 1
        
    search_timer.timeout.connect(on_simulation_step)
    
    def start_mock_search():
        params = analysis_view.control_section.control_widget.get_search_params()
        analysis_view.debug_console.log_message("INFO", f"Triggered search request: {params}")
        
        # Trigger backend start
        engine_manager.start_search(
            depth=params["depth"],
            movetime=params["movetime"],
            nodes=params["nodes"],
            infinite=params["infinite"]
        )
        
        # Reset step count and run mock timer
        search_step[0] = 0
        search_timer.start(1000) # update metrics every second
        analysis_view.debug_console.log_message("INFO", "UCI background search simulation started.")
        
    def stop_mock_search():
        engine_manager.stop_search()
        analysis_view.debug_console.log_message("INFO", "Search aborted by user request.")
        
    def clear_board_triggered():
        analysis_view.debug_console.log_message("INFO", "Clear board action request forwarded.")
        game_controller.highlight_manager.reset()
        analysis_view.move_list.clear()
        analysis_view.clear()
        analysis_view.board.update()
        
    def flip_board_triggered():
        analysis_view.debug_console.log_message("INFO", "Flip board perspective toggle request forwarded.")
        
    # Re-connect buttons to mock search loops
    analysis_view.control_section.new_search_clicked.connect(start_mock_search)
    analysis_view.control_section.stop_clicked.connect(stop_mock_search)
    analysis_view.control_section.clear_board_clicked.connect(clear_board_triggered)
    analysis_view.control_section.flip_board_clicked.connect(flip_board_triggered)
    
    # 5. Handle theme cycling
    def cycle_theme():
        idx = (current_theme_idx[0] + 1) % len(themes_list)
        current_theme_idx[0] = idx
        next_theme_name = themes_list[idx]
        theme_manager.set_theme(next_theme_name)
        next_theme = theme_manager.get_theme()
        
        # Dynamic repainting
        window.setStyleSheet(f"background-color: {next_theme.panel_background.name()};")
        analysis_view.update_theme(next_theme)
        header.setStyleSheet(f"font-family: 'Outfit'; font-size: 16px; font-weight: 800; color: {next_theme.console_in.name()};")
        btn_cycle_theme.setText(f"🎨 Cycle Theme: {next_theme.name}")
        analysis_view.debug_console.log_message("INFO", f"Switched theme configuration to: {next_theme.name}")
        
    btn_cycle_theme.clicked.connect(cycle_theme)
    
    # 6. Chessboard click debug logging
    analysis_view.board.square_clicked.connect(
        lambda sq: analysis_view.debug_console.log_message("INFO", f"Board click coordinates on square index: {sq}")
    )
    
    # Mock some moves at launch
    starting_moves = ["e4", "e5", "Nf3", "Nc6", "Bb5"]
    for move in starting_moves:
        analysis_view.move_list.add_move(move)
        
    analysis_view.debug_console.log_message("INFO", "Master workbench sandbox running. Ready to test inputs and themes!")
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
