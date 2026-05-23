import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Import decoupled visual and controller components matching the ChessBoard pattern
from uci.uci_panel_renderer import UCIPanelRenderer
from uci.uci_controller import UCIController


class UCIPanel(ttk.Frame):
    """
    Structural UI widget representing the UCI engine dashboard panel.
    Delegates visual styles to UCIPanelRenderer and user interactions to UCIController.
    Matches the pattern of ChessBoard in the board folder.
    """
    def __init__(self, parent, theme, **kwargs):
        # Configure fixed width of the panel to prevent auto-resizing clipping
        kwargs.setdefault("width", 420)
        super().__init__(parent, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        self.theme = theme
        self.engine = None
        
        # Local configuration states
        self.custom_moves = []
        self.last_engine_eval = 0.0
        self.last_score_mate = False
        
        # Setup visual renderer and interactive controller
        self.renderer = UCIPanelRenderer(self, theme)
        self.renderer.setup_ttk_styles()
        self.controller = UCIController(self)
        
        # Build UI widget blocks and apply dynamic theme styling
        self.create_widgets()
        self.renderer.apply_theme()
        
    def set_engine(self, engine):
        """
        Gives the panel and its renderer a reference to the active UCI client.
        """
        self.engine = engine
        self.renderer.apply_theme()

    def create_widgets(self):
        # Master scroll or padding layout
        master_pad = ttk.Frame(self, style="ControlPanel.TFrame", padding=10)
        master_pad.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # 1. ENGINE EXECUTABLE PATH CARD
        # ----------------------------------------------------
        path_card = ttk.Frame(master_pad, style="Card.TFrame", padding=10)
        path_card.pack(fill="x", pady=(0, 10))
        
        ttk.Label(path_card, text="ENGINE CONFIGURATION", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))
        
        # Find default/fallback engine executable path
        default_exec = ""
        possible_paths = [
            Path("c:/Users/sidda/Projects/chess-bot-uci-gui/gui/mock_engine.py"),
            Path("c:/Users/sidda/Projects/BluieChessBot/build/BluieChessBot.exe"),
            Path("c:/Users/sidda/Projects/BluieChessBot/gui/uci/mock_engine.py")
        ]
        for p in possible_paths:
            if p.exists():
                default_exec = str(p.resolve())
                break
                
        self.exec_path_var = tk.StringVar(value=default_exec)
        entry_frame = ttk.Frame(path_card, style="Card.TFrame")
        entry_frame.pack(fill="x", pady=2)
        
        self.path_entry = tk.Entry(
            entry_frame, 
            textvariable=self.exec_path_var, 
            font=("Consolas", 9), 
            bd=0
        )
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 5))
        
        self.btn_browse = tk.Button(
            entry_frame, 
            text="Browse", 
            command=self.controller.browse_binary, 
            font=("Segoe UI", 9, "bold"),
            bd=0, 
            padx=10, 
            pady=3
        )
        self.btn_browse.pack(side="right")
        
        # Connection buttons and status indicators
        status_row = ttk.Frame(path_card, style="Card.TFrame")
        status_row.pack(fill="x", pady=(6, 0))
        
        self.btn_connect = tk.Button(
            status_row, 
            text="CONNECT ENGINE", 
            command=self.controller.toggle_engine_connection, 
            font=("Segoe UI", 9, "bold"),
            bd=0, 
            pady=4
        )
        self.btn_connect.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.lbl_status = ttk.Label(status_row, text="🔴 DISCONNECTED", style="StatusDisconnected.TLabel")
        self.lbl_status.pack(side="right", padx=5)

        # ----------------------------------------------------
        # 2. LIVE BOT PERFORMANCE METRICS CARD
        # ----------------------------------------------------
        metrics_card = ttk.Frame(master_pad, style="Card.TFrame", padding=10)
        metrics_card.pack(fill="x", pady=(0, 10))
        
        ttk.Label(metrics_card, text="LIVE BOT PERFORMANCE METRICS", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        
        metrics_grid = ttk.Frame(metrics_card, style="Card.TFrame")
        metrics_grid.pack(fill="x")
        
        # Row 1: Depth and Score
        ttk.Label(metrics_grid, text="Calculated Depth:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_eval_depth = ttk.Label(metrics_grid, text="-", style="CardMetric.TLabel")
        self.lbl_eval_depth.grid(row=0, column=1, sticky="w", padx=(10, 30), pady=2)
        
        ttk.Label(metrics_grid, text="Eval Rating/Score:", style="CardText.TLabel").grid(row=0, column=2, sticky="w", pady=2)
        self.lbl_eval_score = ttk.Label(metrics_grid, text="-", style="CardMetric.TLabel")
        self.lbl_eval_score.grid(row=0, column=3, sticky="w", padx=10, pady=2)
        
        # Row 2: Nodes and NPS
        ttk.Label(metrics_grid, text="Nodes Searched:", style="CardText.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_eval_nodes = ttk.Label(metrics_grid, text="-", style="CardMetric.TLabel")
        self.lbl_eval_nodes.grid(row=1, column=1, sticky="w", padx=(10, 30), pady=2)
        
        ttk.Label(metrics_grid, text="NPS (Nodes/Sec):", style="CardText.TLabel").grid(row=1, column=2, sticky="w", pady=2)
        self.lbl_eval_nps = ttk.Label(metrics_grid, text="-", style="CardMetric.TLabel")
        self.lbl_eval_nps.grid(row=1, column=3, sticky="w", padx=10, pady=2)

        # ----------------------------------------------------
        # 3. ENGINE ACTIONS & OPTION CONFIGURATIONS CARD
        # ----------------------------------------------------
        actions_card = ttk.Frame(master_pad, style="Card.TFrame", padding=10)
        actions_card.pack(fill="x", pady=(0, 10))
        
        ttk.Label(actions_card, text="ENGINE ACTIONS & CONFIGURATIONS", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        
        # Grid of action triggers
        grid_frame = ttk.Frame(actions_card, style="Card.TFrame")
        grid_frame.pack(fill="x", pady=2)
        
        self.btn_inf = tk.Button(
            grid_frame, 
            text="INFINITE", 
            command=lambda: self.controller.send_uci_command("go infinite"),
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            pady=3
        )
        self.btn_inf.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        
        self.btn_halt = tk.Button(
            grid_frame, 
            text="STOP / HALT", 
            command=lambda: self.controller.send_uci_command("stop"),
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            pady=3
        )
        self.btn_halt.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        
        self.btn_ready = tk.Button(
            grid_frame, 
            text="ISREADY", 
            command=lambda: self.controller.send_uci_command("isready"),
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            pady=3
        )
        self.btn_ready.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        
        self.btn_reset = tk.Button(
            grid_frame, 
            text="RESET GAME", 
            command=self.controller.reset_game,
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            pady=3
        )
        self.btn_reset.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        
        # Side-by-side threads & hash parameter configurations
        param_frame = ttk.Frame(actions_card, style="Card.TFrame")
        param_frame.pack(fill="x", pady=(6, 0))
        
        # Thread Spinner
        t_frame = ttk.Frame(param_frame, style="Card.TFrame")
        t_frame.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Label(t_frame, text="Threads:", style="CardText.TLabel").pack(anchor="w")
        self.thread_spin = tk.Spinbox(
            t_frame, 
            from_=1, 
            to=32, 
            width=6, 
            bd=0
        )
        self.thread_spin.delete(0, "end")
        self.thread_spin.insert(0, "4")
        self.thread_spin.pack(fill="x", ipady=2)
        
        # Hash Spinner
        h_frame = ttk.Frame(param_frame, style="Card.TFrame")
        h_frame.pack(side="right", expand=True, fill="x", padx=(4, 0))
        ttk.Label(h_frame, text="Hash (MB):", style="CardText.TLabel").pack(anchor="w")
        self.hash_spin = tk.Spinbox(
            h_frame, 
            from_=16, 
            to=65536, 
            increment=16, 
            width=6, 
            bd=0
        )
        self.hash_spin.delete(0, "end")
        self.hash_spin.insert(0, "128")
        self.hash_spin.pack(fill="x", ipady=2)
        
        # Send options trigger
        self.btn_send_options = tk.Button(
            actions_card, 
            text="Send Engine Configuration Options", 
            command=self.controller.send_options,
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            pady=3
        )
        self.btn_send_options.pack(fill="x", pady=(8, 0))

        # ----------------------------------------------------
        # 4. CUSTOM SEARCH OPTIONS CARD
        # ----------------------------------------------------
        search_card = ttk.Frame(master_pad, style="Card.TFrame", padding=10)
        search_card.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_card, text="CUSTOM SEARCH OPTIONS", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        
        # Depth search row
        depth_row = ttk.Frame(search_card, style="Card.TFrame")
        depth_row.pack(fill="x", pady=2)
        ttk.Label(depth_row, text="Depth:", style="CardText.TLabel").pack(side="left")
        
        self.depth_spin = tk.Spinbox(
            depth_row, 
            from_=1, 
            to=30, 
            width=6, 
            bd=0
        )
        self.depth_spin.delete(0, "end")
        self.depth_spin.insert(0, "10")
        self.depth_spin.pack(side="left", padx=10, ipady=2)
        
        self.btn_go_depth = tk.Button(
            depth_row, 
            text="Go Depth", 
            command=self.controller.go_depth_action,
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            padx=12, 
            pady=2
        )
        self.btn_go_depth.pack(side="right")
        
        # Time search row
        time_row = ttk.Frame(search_card, style="Card.TFrame")
        time_row.pack(fill="x", pady=2)
        ttk.Label(time_row, text="Time(ms):", style="CardText.TLabel").pack(side="left")
        
        self.time_spin = tk.Spinbox(
            time_row, 
            from_=500, 
            to=60000, 
            increment=500, 
            width=6, 
            bd=0
        )
        self.time_spin.delete(0, "end")
        self.time_spin.insert(0, "2000")
        self.time_spin.pack(side="left", padx=10, ipady=2)
        
        self.btn_go_time = tk.Button(
            time_row, 
            text="Go Time", 
            command=self.controller.go_time_action,
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            padx=12, 
            pady=2
        )
        self.btn_go_time.pack(side="right")

        # ----------------------------------------------------
        # 5. RAW UCI LOG MONITOR CARD
        # ----------------------------------------------------
        terminal_card = ttk.Frame(master_pad, style="Card.TFrame", padding=10)
        terminal_card.pack(fill="both", expand=True)
        
        ttk.Label(terminal_card, text="RAW UCI LOG MONITOR", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))
        
        # Scrollable console logger box
        self.log_text = tk.Text(
            terminal_card, 
            bd=0, 
            font=("Consolas", 9), 
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, pady=(0, 6))
        
        # Manual command entry row
        entry_row = ttk.Frame(terminal_card, style="Card.TFrame")
        entry_row.pack(fill="x")
        
        self.cmd_var = tk.StringVar()
        self.cmd_entry = tk.Entry(
            entry_row, 
            textvariable=self.cmd_var, 
            font=("Consolas", 10), 
            bd=0
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 5))
        self.cmd_entry.bind("<Return>", lambda e: self.controller.send_manual_cmd())
        
        self.btn_send = tk.Button(
            entry_row, 
            text="Send", 
            command=self.controller.send_manual_cmd,
            font=("Segoe UI", 9, "bold"), 
            bd=0, 
            padx=12, 
            pady=3
        )
        self.btn_send.pack(side="right")

    # ----------------------------------------------------
    # TELEMETRY AND LOGGING ENGINE CALLBACKS
    # ----------------------------------------------------
    def on_engine_log(self, text, style_tag):
        """Callback: appends standard in/out raw communication to log console."""
        self.log_text.insert(tk.END, text, style_tag)
        self.log_text.see(tk.END)

    def on_engine_info(self, info):
        """Callback: processes parsed engine metrics and updates labels."""
        if "depth" in info:
            self.lbl_eval_depth.config(text=info["depth"])
            
        if "nodes" in info:
            try:
                n = int(info["nodes"])
                self.lbl_eval_nodes.config(text=f"{n:,}")
            except Exception:
                self.lbl_eval_nodes.config(text=info["nodes"])
                
        if "nps" in info:
            try:
                nps_val = int(info["nps"])
                self.lbl_eval_nps.config(text=f"{nps_val:,}")
            except Exception:
                self.lbl_eval_nps.config(text=info["nps"])
                
        if "score_type" in info:
            score_type = info["score_type"]
            score_val = info.get("score_val", "0")
            try:
                v = int(score_val)
                if score_type == "cp":
                    self.last_engine_eval = v / 100.0
                    self.last_score_mate = False
                    prefix = "+" if v >= 0 else ""
                    self.lbl_eval_score.config(text=f"{prefix}{self.last_engine_eval:+.2f} cp")
                else:  # mate
                    self.last_engine_eval = float(v)
                    self.last_score_mate = True
                    prefix = "+" if v >= 0 else "-"
                    self.lbl_eval_score.config(text=f"MATE in {prefix}{abs(v)}")
            except Exception:
                pass

    def on_bestmove(self, best, ponder):
        """Callback: receives and displays search results."""
        ponder_str = f" | ponder: {ponder}" if ponder else ""
        self.on_engine_log(f"💡 Best Response Found: {best}{ponder_str}\n", "sent")
