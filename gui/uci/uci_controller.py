import os
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path

class UCIController:
    """
    Controller for the UCI Panel, handling all user interactions, button commands,
    engine configurations, and manual searches.
    Matches the pattern of BoardController in the board folder.
    """
    def __init__(self, panel):
        self.panel = panel

    @property
    def engine(self):
        """Gets reference to the engine client from the parent panel."""
        return self.panel.engine

    def browse_binary(self):
        """Opens a file selector to locate chess engine binary or script."""
        filetypes = (
            ('Executable / Script', '*.exe;*.py'),
            ('All files', '*.*')
        ) if os.name == 'nt' else (
            ('All files', '*'),
        )
        
        filename = filedialog.askopenfilename(
            title="Locate Chess Bot Binary or Script",
            initialdir=os.getcwd(),
            filetypes=filetypes
        )
        if filename:
            self.panel.exec_path_var.set(str(Path(filename).resolve()))

    def toggle_engine_connection(self):
        """Connects or disconnects the engine subprocess via UCIClient."""
        if not self.engine:
            messagebox.showerror("Error", "UCI Engine Client is not initialized in the application loop.")
            return

        if self.engine.is_running:
            self.engine.stop()
            self.panel.lbl_status.configure(text="🔴 DISCONNECTED", style="StatusDisconnected.TLabel")
            self.panel.btn_connect.configure(text="CONNECT ENGINE")
        else:
            path = self.panel.exec_path_var.get().strip()
            if not path or not os.path.exists(path):
                messagebox.showerror("Error", "Please specify or select a valid chess bot executable binary or script first.")
                return
                
            success = self.engine.start(path)
            if success:
                self.panel.lbl_status.configure(text="🟢 CONNECTED (UCI)", style="StatusConnected.TLabel")
                self.panel.btn_connect.configure(text="DISCONNECT")
                
        # Reactively re-style connection controls on click
        self.panel.renderer.apply_theme()

    def send_uci_command(self, cmd):
        """Sends a standard command line to the engine stdin."""
        if self.engine and self.engine.is_running:
            self.engine.send_command(cmd)
        else:
            self.panel.on_engine_log("⚠️ Command ignored: Chess Engine is not connected.\n", "warning")

    def send_options(self):
        """Transmits performance options configurations to the engine."""
        self.send_uci_command(f"setoption name Threads value {self.panel.thread_spin.get()}")
        self.send_uci_command(f"setoption name Hash value {self.panel.hash_spin.get()}")

    def reset_game(self):
        """Resets the game state locally and triggers engine ucinewgame checks."""
        self.panel.custom_moves = []
        self.panel.lbl_eval_depth.config(text="-")
        self.panel.lbl_eval_score.config(text="-")
        self.panel.lbl_eval_nodes.config(text="-")
        self.panel.lbl_eval_nps.config(text="-")
        
        if self.engine and self.engine.is_running:
            self.engine.send_command("ucinewgame")
            self.engine.send_command("isready")
        else:
            self.panel.on_engine_log("⚠️ Command ignored: Chess Engine is not connected.\n", "warning")

    def go_depth_action(self):
        """Executes a custom depth analysis search."""
        depth = self.panel.depth_spin.get()
        if self.panel.custom_moves:
            self.send_uci_command(f"position startpos moves {' '.join(self.panel.custom_moves)}")
        else:
            self.send_uci_command("position startpos")
        self.send_uci_command(f"go depth {depth}")

    def go_time_action(self):
        """Executes a time-limited analysis search."""
        time_ms = self.panel.time_spin.get()
        if self.panel.custom_moves:
            self.send_uci_command(f"position startpos moves {' '.join(self.panel.custom_moves)}")
        else:
            self.send_uci_command("position startpos")
        self.send_uci_command(f"go movetime {time_ms}")

    def send_manual_cmd(self):
        """Sends custom commands written in the raw log console entry box."""
        cmd = self.panel.cmd_var.get().strip()
        if cmd:
            self.send_uci_command(cmd)
            self.panel.cmd_var.set("")
