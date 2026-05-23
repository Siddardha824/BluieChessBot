import tkinter as tk
from tkinter import ttk

from themes.theme_manager import ThemeManager
from board.chessboard import ChessBoard

# Import newly created modular UCI components
from uci.uci_client import UCIClient
from uci.uci_panel import UCIPanel


class BluieApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Bluie Chess Bot Workspace")

        # Cap window dimensions and set to maximized state
        self.geometry("1300x800")
        self.state("zoomed")

        self.theme_manager = ThemeManager()
        self.theme = self.theme_manager.get_theme()
        
        self.configure(bg=self.theme.WINDOW_BG)
        
        # Configure overall style background color for standard TFrames
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=self.theme.WINDOW_BG)

        # ----------------------------------------------------
        # HORIZONTAL SIDE-BY-SIDE LAYOUT CREATION
        # ----------------------------------------------------
        layout_container = ttk.Frame(self, style="TFrame")
        layout_container.pack(fill="both", expand=True)

        # Left Column: ChessBoard Canvas
        self.board = ChessBoard(layout_container, self.theme)
        self.board.pack(
            side="left",
            expand=True,
            fill="both",
            padx=20,
            pady=20
        )

        # Right Column: Dedicated UCI Control Panel Widget (Fixed Width)
        self.control_panel = UCIPanel(layout_container, self.theme)
        self.control_panel.pack(
            side="right",
            fill="both",
            padx=(0, 20),
            pady=20
        )

        # ----------------------------------------------------
        # UCI ENGINE CLIENT & CALLBACK SETUP
        # ----------------------------------------------------
        self.engine = UCIClient(
            log_callback=self.control_panel.on_engine_log,
            info_callback=self.control_panel.on_engine_info,
            bestmove_callback=self.control_panel.on_bestmove
        )
        
        # Connect control panel to client reference
        self.control_panel.set_engine(self.engine)

        # Start periodic thread-safe queue updates polling loop
        self.update_engine_queue()

        # Handle clean exit of child engine subprocess if main window is closed
        def on_close():
            self.engine.stop()
            self.destroy()
            
        self.protocol("WM_DELETE_WINDOW", on_close)

    def update_engine_queue(self):
        """
        Polls the engine process's stdout queue periodically via Tkinter main loop.
        """
        self.engine.update()
        self.after(50, self.update_engine_queue)