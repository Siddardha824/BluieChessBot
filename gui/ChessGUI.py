#!/usr/bin/env python3
"""
C++ Chess Bot Debugger & UCI GUI
---------------------------------
An offline development and debugging tool for C++ UCI chess bots.
Built entirely using Python's standard library (tkinter, subprocess, threading, queue).
No external dependencies required!
"""

import os
import sys

# Enable High-DPI awareness on Windows before importing tkinter or constructing any widgets
if os.name == 'nt':
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # Per-monitor DPI aware
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1) # System DPI aware
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware() # Vista/7 fallback
            except Exception:
                pass

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Import refactored modules
from constants import (
    PIECE_CHARS,
    DEFAULT_BOARD,
    STARTING_FEN,
    BOARD_THEMES,
    CPP_TEMPLATE_CODE,
    MOCK_ENGINE_CODE
)
from engine_connector import UCIEngineConnector
from board_view import EvaluationBar, ChessBoardCanvas


class ChessGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("C++ UCI Chess Bot Debugger Workspace")
        
        # Determine the DPI scale factor
        try:
            dpi = self.winfo_fpixels('1i')
            self.dpi_scale = dpi / 96.0
        except Exception:
            self.dpi_scale = 1.0

        # Adjust window size to fit screen boundaries
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Target geometry scaled by DPI
        target_w = int(1250 * self.dpi_scale)
        target_h = int(920 * self.dpi_scale)

        # Cap window dimensions to prevent clipping on scaled laptops
        w = min(target_w, int(screen_width * 0.95))
        h = min(target_h, int(screen_height * 0.90))

        self.geometry(f"{w}x{h}")
        self.configure(bg="#0f172a") # Dark Slate Theme matching frosted-glass accent
        
        # Grid layout state
        # Dynamically scale tile size according to the window height
        self.tile_size = max(60, min(120, int((h - 280) // 8)))
        self.selected_square = None # (row, col)
        self.dragged_piece = None
        self.drag_start_square = None
        self.drag_x = 0
        self.drag_y = 0
        self.custom_moves = []
        self.current_fen = STARTING_FEN
        self.board_state = [row[:] for row in DEFAULT_BOARD]
        self.selected_brush = tk.StringVar(value="move") # "move", "erase", or piece char
        self.active_theme_name = tk.StringVar(value="Bluie Teal")
        self.last_move_squares = [] # [(r1, c1), (r2, c2)] to highlight
        self.last_engine_eval = 0.0 # float cp score for visual eval bar (e.g. +1.5, -0.3)
        self.last_score_mate = False # True if mate score
        
        # Sprite Sheet Configuration
        self.use_sprites = tk.BooleanVar(value=True)
        
        # Select best default sprite path based on current folder
        default_sprite = "assets/Pieces.png"
        if not os.path.exists(default_sprite):
            if os.path.exists("Pieces.png"):
                default_sprite = "Pieces.png"
        self.sprite_path_var = tk.StringVar(value=default_sprite)
        self.piece_sprites = {}
        
        # Configure styles
        self.setup_styles()
        
        # Initialize engine connector
        self.engine = UCIEngineConnector(
            log_callback=self.on_engine_log,
            info_callback=self.on_engine_info,
            bestmove_callback=self.on_bestmove
        )
        
        # Build UI
        self.create_widgets()
        
        # Load piece sprites using refactored canvas helper
        self.canvas.load_piece_sprites()
        
        # Sync board with starting FEN and apply initial theme colors
        self.parse_fen(self.current_fen)
        self.on_theme_change()
        
        # Start periodic update timer for read queue
        self.update_engine_queue()

    def browse_sprite_sheet(self):
        filename = filedialog.askopenfilename(
            title="Select Chess Pieces Sprite Sheet PNG",
            initialdir=os.getcwd(),
            filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
        )
        if filename:
            self.sprite_path_var.set(filename)
            if self.canvas.load_piece_sprites():
                self.lbl_sprite_status.config(text=f"{os.path.basename(filename)}: Loaded", foreground="#34d399")
                self.use_sprites.set(True)
            else:
                self.lbl_sprite_status.config(text="Load Failed", foreground="#f87171")
                self.use_sprites.set(False)
            self.canvas.draw()

    def on_sprite_toggle(self):
        if self.use_sprites.get():
            if not self.piece_sprites:
                if not self.canvas.load_piece_sprites():
                    self.use_sprites.set(False)
                    messagebox.showerror("Error", "Could not load sprite sheet. Falling back to Unicode.")
        self.canvas.draw()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Read the active theme configurations dynamically
        theme_name = self.active_theme_name.get() if hasattr(self, "active_theme_name") else "Bluie Teal"
        cfg = BOARD_THEMES.get(theme_name, BOARD_THEMES["Bluie Teal"])
        
        # Elegant theme-based controls
        style.configure("TFrame", background=cfg["bg_dark"])
        style.configure("Header.TFrame", background=cfg["bg_mid"], borderwidth=1, relief="solid")
        style.configure("Card.TFrame", background=cfg["bg_mid"], relief="flat")
        
        style.configure("TLabel", background=cfg["bg_dark"], foreground=cfg["fg"], font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=cfg["bg_mid"], foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        style.configure("Section.TLabel", background=cfg["bg_mid"], foreground="#94a3b8", font=("Segoe UI", 9, "bold"))
        style.configure("Console.TLabel", background=cfg["bg_dark"], foreground=cfg["accent"], font=("Consolas", 9))
        
        style.configure("TEntry", fieldbackground="#090d16", foreground=cfg["fg"], insertcolor=cfg["accent"])
        
        # Configure and explicitly map TCombobox states for 'readonly' and focused states
        style.configure("TCombobox", fieldbackground="#090d16", background=cfg["bg_mid"], foreground=cfg["fg"])
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#090d16")],
                  selectbackground=[("readonly", "#090d16")],
                  selectforeground=[("readonly", cfg["fg"])],
                  foreground=[("readonly", cfg["fg"])],
                  background=[("readonly", cfg["bg_mid"])])
        
        # Configure Option Database for popdown Listbox to follow active theme colors
        self.option_add("*TCombobox*Listbox.background", "#090d16")
        self.option_add("*TCombobox*Listbox.foreground", cfg["fg"])
        self.option_add("*TCombobox*Listbox.selectBackground", cfg["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        
        # Bottom Notebook Styling
        style.configure("TNotebook", background=cfg["bg_dark"], borderwidth=0)
        style.configure("TNotebook.Tab", background=cfg["bg_mid"], foreground="#94a3b8", font=("Segoe UI", 9, "bold"), padding=6)
        style.map("TNotebook.Tab", 
                  background=[("selected", "#090d16")], 
                  foreground=[("selected", cfg["accent"])])
        
        # Button styling
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6, background=cfg["accent"], foreground="#ffffff")
        style.map("TButton",
            background=[("active", cfg["accent"]), ("disabled", "#475569")],
            foreground=[("active", "#ffffff"), ("disabled", "#94a3b8")]
        )
        
        style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), padding=6, background="#10b981", foreground="#ffffff")
        style.map("Accent.TButton",
            background=[("active", "#059669")]
        )

        style.configure("Halt.TButton", font=("Segoe UI", 9, "bold"), padding=6, background="#ef4444", foreground="#ffffff")
        style.map("Halt.TButton",
            background=[("active", "#dc2626")]
        )

    def create_widgets(self):
        # 1. Header Frame (Frosted Title / Connection State)
        header_frame = ttk.Frame(self, style="Header.TFrame", padding=10)
        header_frame.pack(fill="x", side="top", padx=10, pady=(10, 5))
        
        logo_label = ttk.Label(header_frame, text="♘ C++ BOT DEBUGGER (BLUIE)", font=("Segoe UI", 14, "bold"), background="#1e293b", foreground="#60a5fa")
        logo_label.pack(side="left", padx=5)
        
        status_sub = ttk.Label(header_frame, text="UCI-PROTOCOL COMPANION", font=("Courier", 10, "bold"), background="#1e293b", foreground="#64748b")
        status_sub.pack(side="left", padx=10)
        
        self.connection_status_lbl = ttk.Label(header_frame, text="🔴 DISCONNECTED", font=("Segoe UI", 10, "bold"), background="#1e293b", foreground="#f87171")
        self.connection_status_lbl.pack(side="right", padx=15)
        
        # Main client division
        main_content = ttk.Frame(self, style="TFrame")
        main_content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # LEFT COLUMN: Config and Controls
        left_col = ttk.Frame(main_content, style="TFrame", width=280)
        left_col.pack(side="left", fill="y", padx=(0, 5))
        left_col.pack_propagate(False)
        
        # Sidebar section: Executable Selector
        path_card = ttk.Frame(left_col, style="Card.TFrame", padding=6, borderwidth=1, relief="solid")
        path_card.pack(fill="x", pady=(0, 6))
        ttk.Label(path_card, text="BOT EXECUTABLE PATH", style="Section.TLabel").pack(anchor="w", pady=(0, 2))
        
        # Intelligent executable selection
        default_engine = "../build/BluieChessBot.exe"
        if not os.path.exists(default_engine):
            if os.path.exists("build/BluieChessBot.exe"):
                default_engine = "build/BluieChessBot.exe"
            elif os.path.exists("BluieChessBot.exe"):
                default_engine = "BluieChessBot.exe"
            elif os.path.exists("./mock_engine.py"):
                default_engine = "./mock_engine.py"
            elif os.path.exists("mock_engine.py"):
                default_engine = "mock_engine.py"
            else:
                default_engine = "./mock_engine.py"
                
        self.path_var = tk.StringVar(value=default_engine)
        path_entry = ttk.Entry(path_card, textvariable=self.path_var, font=("Segoe UI", 9))
        path_entry.pack(fill="x", pady=2)
        
        btn_frame = ttk.Frame(path_card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(2, 0))
        btn_browse = ttk.Button(btn_frame, text="Browse", command=self.browse_binary, width=10)
        btn_browse.pack(side="left", expand=True, fill="x", padx=(0, 2))
        self.btn_connect = ttk.Button(btn_frame, text="Connect", command=self.toggle_engine_connection, width=12)
        self.btn_connect.pack(side="right", expand=True, fill="x", padx=(2, 0))
        
        # Sidebar section: Engine Controls & Param parameters in a unified card
        ctrl_card = ttk.Frame(left_col, style="Card.TFrame", padding=6, borderwidth=1, relief="solid")
        ctrl_card.pack(fill="x", pady=(0, 6))
        ttk.Label(ctrl_card, text="ENGINE CONTROLS & PARAMS", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        
        grid_frame = ttk.Frame(ctrl_card, style="Card.TFrame")
        grid_frame.pack(fill="x", pady=2)
        
        btn_inf = ttk.Button(grid_frame, text="INFINITE", style="Accent.TButton", command=lambda: self.send_uci_command("go infinite"), width=12)
        btn_inf.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        btn_halt = ttk.Button(grid_frame, text="STOP / HALT", style="Halt.TButton", command=lambda: self.send_uci_command("stop"), width=12)
        btn_halt.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        btn_reset = ttk.Button(grid_frame, text="RESET GAME", command=self.reset_game, width=12)
        btn_reset.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        btn_ready = ttk.Button(grid_frame, text="ISREADY", command=lambda: self.send_uci_command("isready"), width=12)
        btn_ready.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        
        # Parameters side-by-side in grid
        param_frame = ttk.Frame(ctrl_card, style="Card.TFrame")
        param_frame.pack(fill="x", pady=4)
        
        # Threads
        t_frame = ttk.Frame(param_frame, style="Card.TFrame")
        t_frame.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Label(t_frame, text="Threads:", font=("Segoe UI", 8), background="#1e293b", foreground="#94a3b8").pack(anchor="w")
        self.thread_spin = ttk.Spinbox(t_frame, from_=1, to=32, width=6)
        self.thread_spin.set(4)
        self.thread_spin.pack(fill="x")
        
        # Hash
        h_frame = ttk.Frame(param_frame, style="Card.TFrame")
        h_frame.pack(side="right", expand=True, fill="x", padx=(4, 0))
        ttk.Label(h_frame, text="Hash (MB):", font=("Segoe UI", 8), background="#1e293b", foreground="#94a3b8").pack(anchor="w")
        self.hash_spin = ttk.Spinbox(h_frame, from_=16, to=65536, increment=16, width=6)
        self.hash_spin.set(128)
        self.hash_spin.pack(fill="x")
        
        ttk.Button(ctrl_card, text="Send Engine Configuration", command=self.send_options).pack(fill="x", pady=(2, 0))
        
        # Sidebar section: Theme, Preset FENs and Sprite loaders
        preset_card = ttk.Frame(left_col, style="Card.TFrame", padding=6, borderwidth=1, relief="solid")
        preset_card.pack(fill="x", pady=(0, 6))
        ttk.Label(preset_card, text="BOARD PRESETS & THEMES", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        
        # Dropdowns side-by-side
        drop_frame = ttk.Frame(preset_card, style="Card.TFrame")
        drop_frame.pack(fill="x", pady=2)
        
        theme_f = ttk.Frame(drop_frame, style="Card.TFrame")
        theme_f.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Label(theme_f, text="Theme:", font=("Segoe UI", 8), background="#1e293b", foreground="#94a3b8").pack(anchor="w")
        self.theme_cb = ttk.Combobox(theme_f, textvariable=self.active_theme_name, state="readonly", values=["Classic Emerald", "Deep Velvet", "Nordic Ice", "High Contrast Dark", "Bluie Teal"], width=12)
        self.theme_cb.set("Bluie Teal")
        self.theme_cb.pack(fill="x")
        self.theme_cb.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        pres_f = ttk.Frame(drop_frame, style="Card.TFrame")
        pres_f.pack(side="right", expand=True, fill="x", padx=(4, 0))
        ttk.Label(pres_f, text="Presets:", font=("Segoe UI", 8), background="#1e293b", foreground="#94a3b8").pack(anchor="w")
        self.preset_var = tk.StringVar()
        self.preset_cb = ttk.Combobox(pres_f, textvariable=self.preset_var, state="readonly", values=[
            "Starting Position",
            "Ruy Lopez (Opening)",
            "Sicilian Defense (Opening)",
            "Queen's Gambit (Opening)",
            "K+Q Endgame Study",
            "Rook & Pawn Study",
            "Tactical Fork Puzzle"
        ], width=12)
        self.preset_cb.set("Starting Position")
        self.preset_cb.pack(fill="x")
        self.preset_cb.bind("<<ComboboxSelected>>", self.on_preset_select)
        
        # Checkbox & Loader for custom piece sprites
        sprite_f = ttk.Frame(preset_card, style="Card.TFrame")
        sprite_f.pack(fill="x", pady=(4, 0))
        
        sprite_cb = tk.Checkbutton(
            sprite_f, 
            text="Use Sprites", 
            variable=self.use_sprites,
            command=self.on_sprite_toggle,
            bg="#1e293b",
            fg="#e2e8f0",
            selectcolor="#0f172a",
            activebackground="#1e293b",
            activeforeground="#ffffff",
            font=("Segoe UI", 9),
            bd=0,
            highlightthickness=0
        )
        sprite_cb.pack(side="left")
        
        btn_browse_sprite = ttk.Button(sprite_f, text="Load PNG", command=self.browse_sprite_sheet, width=9)
        btn_browse_sprite.pack(side="right")
        
        sprite_status_text = "Pieces.png: Loaded" if self.piece_sprites else "Pieces.png: Missing"
        sprite_status_color = "#34d399" if self.piece_sprites else "#f87171"
        self.lbl_sprite_status = ttk.Label(preset_card, text=sprite_status_text, font=("Segoe UI", 8, "italic"), background="#1e293b", foreground=sprite_status_color)
        self.lbl_sprite_status.pack(anchor="w", pady=(2, 0))
        
        # Sidebar section: Custom search and Go tools
        go_card = ttk.Frame(left_col, style="Card.TFrame", padding=6, borderwidth=1, relief="solid")
        go_card.pack(fill="x", expand=True)
        ttk.Label(go_card, text="CUSTOM SEARCH OPTIONS", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        
        go_depth_f = ttk.Frame(go_card, style="Card.TFrame")
        go_depth_f.pack(fill="x", pady=2)
        self.go_depth_var = tk.StringVar(value="10")
        ttk.Label(go_depth_f, text="Depth:", font=("Segoe UI", 9), background="#1e293b", foreground="#e2e8f0").pack(side="left", padx=(0,5))
        depth_spin = ttk.Spinbox(go_depth_f, from_=1, to=30, width=5, textvariable=self.go_depth_var)
        depth_spin.pack(side="left")
        btn_go_depth = ttk.Button(go_depth_f, text="Go Depth", command=self.go_depth_action, width=10)
        btn_go_depth.pack(side="right")
        
        go_time_f = ttk.Frame(go_card, style="Card.TFrame")
        go_time_f.pack(fill="x", pady=2)
        self.go_time_var = tk.StringVar(value="2000")
        ttk.Label(go_time_f, text="Time(ms):", font=("Segoe UI", 9), background="#1e293b", foreground="#e2e8f0").pack(side="left", padx=(0,5))
        time_spin = ttk.Spinbox(go_time_f, from_=500, to=60000, increment=500, width=5, textvariable=self.go_time_var)
        time_spin.pack(side="left")
        btn_go_time = ttk.Button(go_time_f, text="Go Time", command=self.go_time_action, width=10)
        btn_go_time.pack(side="right")
        
        # MIDDLE COLUMN: Chessboard Display & Move History
        mid_col = ttk.Frame(main_content, style="TFrame")
        mid_col.pack(side="left", fill="both", expand=True, padx=5)
        
        board_container = ttk.Frame(mid_col, style="Card.TFrame", padding=15, borderwidth=1, relief="solid")
        board_container.pack(fill="both", expand=True)
        
        # Sub-frame for evaluation bar and board canvas side-by-side
        board_row_frame = ttk.Frame(board_container, style="Card.TFrame")
        board_row_frame.pack(fill="both", expand=True, pady=5)
        
        # Tall split-metric visual evaluation bar (22px wide, matching board height)
        self.eval_canvas = EvaluationBar(board_row_frame, self, bg="#1e293b")
        self.eval_canvas.pack(side="left", padx=(0, 10))
        
        # Canvas chessboard
        self.canvas = ChessBoardCanvas(board_row_frame, self, bg="#1e293b")
        self.canvas.pack(side="left", expand=True)
        
        # FEN Input / Output Block
        fen_frame = ttk.Frame(board_container, style="Card.TFrame")
        fen_frame.pack(fill="x", pady=5)
        ttk.Label(fen_frame, text="Active FEN string:", font=("Segoe UI", 8, "bold"), background="#1e293b", foreground="#94a3b8").pack(anchor="w")
        
        self.fen_var = tk.StringVar(value=self.current_fen)
        fen_entry = ttk.Entry(fen_frame, textvariable=self.fen_var, font=("Consolas", 10), background="#0f172a")
        fen_entry.pack(fill="x", side="left", expand=True, padx=(0, 5))
        
        btn_apply_fen = ttk.Button(fen_frame, text="Apply FEN", command=self.apply_fen_click)
        btn_apply_fen.pack(side="right")
        
        # Custom Moves History & Best Move suggest labels
        status_bar = ttk.Frame(board_container, style="Card.TFrame", padding=5)
        status_bar.pack(fill="x")
        
        self.lbl_bestmove = ttk.Label(status_bar, text="💡 Best response: Pending engine request", font=("Segoe UI", 10, "bold"), background="#1e293b", foreground="#38bdf8")
        self.lbl_bestmove.pack(anchor="w", pady=2)
        
        self.lbl_moves = ttk.Label(status_bar, text="Moves sent: none", font=("Segoe UI", 8, "italic"), background="#1e293b", foreground="#94a3b8")
        self.lbl_moves.pack(anchor="w", pady=2)

        # 🎨 Sandbox Piece Paintbrush Palette Toolbar below moves
        palette_frame = ttk.Frame(board_container, style="Card.TFrame", padding=5)
        palette_frame.pack(fill="x", pady=5)
        
        ttk.Label(palette_frame, text="🎨 Sandbox Placement Brush:", font=("Segoe UI", 9, "bold"), background="#1e293b", foreground="#94a3b8").pack(anchor="w", pady=(0, 5))
        
        brush_buttons_frame = ttk.Frame(palette_frame, style="Card.TFrame")
        brush_buttons_frame.pack(fill="x")
        
        brushes = [
            ("Move 🖲️", "move"), ("Erase ⌫", "erase"),
            ("♙", "P"), ("♘", "N"), ("♗", "B"), ("♖", "R"), ("♕", "Q"), ("♔", "K"),
            ("♟", "p"), ("♞", "n"), ("♝", "b"), ("♜", "r"), ("♛", "q"), ("♚", "k")
        ]
        
        for text, value in brushes:
            color = "#38bdf8" if value in ["move", "erase"] else ("#f8fafc" if value.isupper() else "#c084fc")
            rb = tk.Radiobutton(
                brush_buttons_frame,
                text=text,
                variable=self.selected_brush,
                value=value,
                indicatoron=0,
                font=("Segoe UI", 10, "bold"),
                bg="#090d16",
                fg=color,
                selectcolor="#334155",
                activebackground="#1e293b",
                activeforeground=color,
                relief="flat",
                bd=1,
                padx=5,
                pady=1
            )
            rb.pack(side="left", padx=2)

        # RIGHT COLUMN: Dual pane evaluations & raw output terminal
        right_col = ttk.Frame(main_content, style="TFrame", width=380)
        right_col.pack(side="right", fill="both", padx=(5, 0))
        right_col.pack_propagate(False)
        
        # Metrics Panel
        metrics_panel = ttk.Frame(right_col, style="Card.TFrame", padding=10, borderwidth=1, relief="solid")
        metrics_panel.pack(fill="x", pady=(0, 10))
        ttk.Label(metrics_panel, text="LIVE BOT PERFORMANCE METRICS", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        
        # Create metric value fields
        metrics_grid = ttk.Frame(metrics_panel, style="Card.TFrame")
        metrics_grid.pack(fill="x")
        
        ttk.Label(metrics_grid, text="Calculated Depth:", font=("Segoe UI", 9), background="#1e293b", foreground="#94a3b8").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_eval_depth = ttk.Label(metrics_grid, text="-", font=("Consolas", 10, "bold"), background="#1e293b", foreground="#ffffff")
        self.lbl_eval_depth.grid(row=0, column=1, sticky="w", padx=10, pady=2)
        
        ttk.Label(metrics_grid, text="Eval Rating/Score:", font=("Segoe UI", 9), background="#1e293b", foreground="#94a3b8").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_eval_score = ttk.Label(metrics_grid, text="-", font=("Consolas", 10, "bold"), background="#1e293b", foreground="#10b981")
        self.lbl_eval_score.grid(row=1, column=1, sticky="w", padx=10, pady=2)
        
        ttk.Label(metrics_grid, text="Nodes Searched:", font=("Segoe UI", 9), background="#1e293b", foreground="#94a3b8").grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_eval_nodes = ttk.Label(metrics_grid, text="-", font=("Consolas", 10, "bold"), background="#1e293b", foreground="#ffffff")
        self.lbl_eval_nodes.grid(row=2, column=1, sticky="w", padx=10, pady=2)
        
        ttk.Label(metrics_grid, text="NPS (Nodes/Sec):", font=("Segoe UI", 9), background="#1e293b", foreground="#94a3b8").grid(row=3, column=0, sticky="w", pady=2)
        self.lbl_eval_nps = ttk.Label(metrics_grid, text="-", font=("Consolas", 10, "bold"), background="#1e293b", foreground="#ffffff")
        self.lbl_eval_nps.grid(row=3, column=1, sticky="w", padx=10, pady=2)
        
        # Raw Command log file terminal
        terminal_panel = ttk.Frame(right_col, style="Card.TFrame", padding=10, borderwidth=1, relief="solid")
        terminal_panel.pack(fill="both", expand=True)
        ttk.Label(terminal_panel, text="RAW UCI LOG MONITOR", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        
        # Scrollable output log text
        self.log_text = tk.Text(terminal_panel, bg="#090d16", fg="#f1f5f9", font=("Consolas", 9), borderwidth=0, highlightthickness=0, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        
        # Setup tags for colored logs
        self.log_text.tag_config("sent", foreground="#60a5fa")      # Blue
        self.log_text.tag_config("received", foreground="#e2e8f0")  # Light gray
        self.log_text.tag_config("error", foreground="#f87171")     # Red
        self.log_text.tag_config("warning", foreground="#fbbf24")   # Amber
        
        # Fast custom command sender inside Terminal panel
        cmd_sender_frame = ttk.Frame(terminal_panel, style="Card.TFrame", padding=(0, 5, 0, 0))
        cmd_sender_frame.pack(fill="x")
        
        self.cmd_var = tk.StringVar()
        cmd_entry = ttk.Entry(cmd_sender_frame, textvariable=self.cmd_var, font=("Consolas", 10))
        cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        cmd_entry.bind("<Return>", lambda e: self.send_manual_cmd())
        
        btn_send = ttk.Button(cmd_sender_frame, text="Send", command=self.send_manual_cmd)
        btn_send.pack(side="right")

        # Bottom downloads and workspace panel
        downloads_panel = ttk.Frame(self, style="Header.TFrame", padding=12, borderwidth=1, relief="solid")
        downloads_panel.pack(fill="both", expand=True, side="bottom", padx=10, pady=(0, 10))
        
        downloads_header = ttk.Frame(downloads_panel, style="Card.TFrame")
        downloads_header.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            downloads_header, 
            text="💾 Workspace Downloads & C++ Source Templates", 
            font=("Segoe UI", 11, "bold"), 
            background="#1e293b", 
            foreground="#ffffff"
        ).pack(side="left")
        
        ttk.Label(
            downloads_header, 
            text="Copy or export production-ready starter templates to run locally.", 
            font=("Segoe UI", 8, "italic"), 
            background="#1e293b", 
            foreground="#94a3b8"
        ).pack(side="left", padx=15)
        
        # Notebook for files
        self.notebook = ttk.Notebook(downloads_panel)
        self.notebook.pack(fill="both", expand=True, pady=5)
        
        # Tabs for Bot Template and Mock Engine
        self.cpp_tab = ttk.Frame(self.notebook, style="Card.TFrame")
        self.mock_tab = ttk.Frame(self.notebook, style="Card.TFrame")
        
        self.notebook.add(self.cpp_tab, text=" bot_template.cpp ")
        self.notebook.add(self.mock_tab, text=" mock_engine.py ")
        
        self.build_code_tab(self.cpp_tab, CPP_TEMPLATE_CODE, "bot_template.cpp")
        self.build_code_tab(self.mock_tab, MOCK_ENGINE_CODE, "mock_engine.py")

    def build_code_tab(self, parent_frame, code_text, default_filename):
        toolbar = ttk.Frame(parent_frame, style="Card.TFrame", padding=5)
        toolbar.pack(fill="x", side="top")
        
        text_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        code_box = tk.Text(
            text_frame, 
            bg="#090d16", 
            fg="#f1f5f9", 
            font=("Consolas", 9), 
            yscrollcommand=scrollbar.set,
            borderwidth=0,
            highlightthickness=0,
            wrap="none",
            height=8
        )
        code_box.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=code_box.yview)
        code_box.insert(tk.END, code_text)
        code_box.config(state="disabled")
        
        btn_copy = ttk.Button(
            toolbar, 
            text="📋 Copy Source", 
            command=lambda: self.copy_to_clipboard(code_text),
            width=15
        )
        btn_copy.pack(side="right", padx=5)
        
        btn_export = ttk.Button(
            toolbar, 
            text="⬇️ Export File", 
            command=lambda: self.export_source_file(code_text, default_filename),
            width=15
        )
        btn_export.pack(side="right", padx=5)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        messagebox.showinfo("Clipboard", "Code copied to clipboard successfully!")

    def export_source_file(self, text, default_filename):
        filename = filedialog.asksaveasfilename(
            title="Export Source File",
            initialfile=default_filename,
            initialdir=os.getcwd(),
            filetypes=(("Source Files", f"*{os.path.splitext(default_filename)[1]}"), ("All files", "*.*"))
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Success", f"File exported successfully to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export file:\n{str(e)}")

    def on_theme_change(self, event=None):
        self.setup_styles()
        theme_name = self.active_theme_name.get()
        cfg = BOARD_THEMES.get(theme_name, BOARD_THEMES["Classic Emerald"])
        
        # Apply window-level styling updates
        self.configure(bg=cfg["bg_dark"])
        self.canvas.config(bg=cfg["bg_dark"])
        self.eval_canvas.config(bg=cfg["bg_dark"])
        
        # Recursively update all child widgets to follow theme colors
        self.update_all_widget_colors(self, cfg)
        
        # Dynamically change the dropdown Listbox popdown colors for both comboboxes
        if hasattr(self, "theme_cb") and hasattr(self, "preset_cb"):
            for cb in [self.theme_cb, self.preset_cb]:
                try:
                    popdown_listbox = f"[ttk::combobox::PopdownWindow {cb}].f.l"
                    self.tk.eval(
                        f"{popdown_listbox} configure "
                        f"-background #090d16 "
                        f"-foreground {cfg['fg']} "
                        f"-selectbackground {cfg['accent']} "
                        f"-selectforeground #ffffff"
                    )
                except Exception:
                    pass
        
        # Redraw components
        self.canvas.draw()
        self.eval_canvas.draw()

    def update_all_widget_colors(self, widget, cfg):
        try:
            widget_class = widget.winfo_class()
        except Exception:
            return
            
        # Try to read current background/foreground to identify overrides
        bg = None
        try:
            bg = widget.cget("background")
        except Exception:
            pass
            
        fg = None
        try:
            fg = widget.cget("foreground")
        except Exception:
            pass
            
        # 1. Update standard Frame/Label overrides
        if widget_class in ["Frame", "TFrame", "Label", "TLabel"]:
            if bg in ["#1e293b", "#1E293B"]:
                widget.configure(background=cfg["bg_mid"])
            elif bg in ["#0f172a", "#0F172A"]:
                widget.configure(background=cfg["bg_dark"])
                
            if fg == "#94a3b8":
                widget.configure(foreground=cfg["fg"])
            elif fg in ["#38bdf8", "#60a5fa"]:
                widget.configure(foreground=cfg["accent"])
            elif fg == "#e2e8f0":
                widget.configure(foreground=cfg["fg"])
                
        # 2. Update custom radiobuttons in Sandbox or other screens
        elif widget_class in ["Radiobutton", "Checkbutton"]:
            try:
                widget.configure(
                    bg=cfg["bg_mid"],
                    fg=cfg["fg"],
                    activebackground=cfg["bg_mid"],
                    activeforeground=cfg["accent"],
                    selectcolor=cfg["bg_dark"]
                )
            except Exception:
                pass
                
        # 3. Update Textboxes
        elif widget_class == "Text":
            try:
                widget.configure(
                    bg=cfg["bg_dark"] if widget == self.log_text else "#090d16",
                    fg=cfg["fg"],
                    insertbackground=cfg["accent"]
                )
                if widget == self.log_text:
                    widget.tag_config("sent", foreground=cfg["accent"])
                    widget.tag_config("received", foreground=cfg["fg"])
            except Exception:
                pass
                
        # 4. Canvas overrides
        elif widget_class == "Canvas":
            if widget == self.canvas or widget == self.eval_canvas:
                widget.configure(bg=cfg["bg_dark"])
                
        # Traverse recursively
        for child in widget.winfo_children():
            self.update_all_widget_colors(child, cfg)

    # Delegate helper methods to ChessBoardCanvas
    def parse_fen(self, fen):
        return self.canvas.parse_fen(fen)

    def generate_fen(self):
        return self.canvas.generate_fen()

    def draw_board(self):
        self.canvas.draw()

    def draw_eval_bar(self):
        self.eval_canvas.draw()

    def on_sandbox_change(self):
        self.selected_square = None
        self.custom_moves = []
        self.lbl_moves.config(text="Moves sent: none")
        self.current_fen = self.generate_fen()
        self.fen_var.set(self.current_fen)
        if self.engine.is_running:
            self.engine.send_command(f"position fen {self.current_fen}")

    def on_preset_select(self, event=None):
        name = self.preset_var.get()
        presets = {
            "Starting Position": STARTING_FEN,
            "Ruy Lopez (Opening)": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 3",
            "Sicilian Defense (Opening)": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
            "Queen's Gambit (Opening)": "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq d3 0 2",
            "K+Q Endgame Study": "k7/8/1Q6/8/8/8/8/4K3 w - - 0 1",
            "Rook & Pawn Study": "8/k7/3P4/8/8/8/8/1R2K3 w - - 0 1",
            "Tactical Fork Puzzle": "r3k2r/ppq2p1p/2p1bp2/2b1p3/2N1P3/2P2N2/PP2QPPP/2KR3R b kq - 0 1"
        }
        fen = presets.get(name, STARTING_FEN)
        self.fen_var.set(fen)
        self.apply_fen_click()

    def go_depth_action(self):
        depth = self.go_depth_var.get()
        if self.custom_moves:
            if self.current_fen == STARTING_FEN or not self.current_fen:
                self.send_uci_command(f"position startpos moves {' '.join(self.custom_moves)}")
            else:
                self.send_uci_command(f"position fen {self.current_fen} moves {' '.join(self.custom_moves)}")
        else:
            self.send_uci_command(f"position fen {self.current_fen}")
        self.send_uci_command(f"go depth {depth}")

    def go_time_action(self):
        time = self.go_time_var.get()
        if self.custom_moves:
            if self.current_fen == STARTING_FEN or not self.current_fen:
                self.send_uci_command(f"position startpos moves {' '.join(self.custom_moves)}")
            else:
                self.send_uci_command(f"position fen {self.current_fen} moves {' '.join(self.custom_moves)}")
        else:
            self.send_uci_command(f"position fen {self.current_fen}")
        self.send_uci_command(f"go movetime {time}")

    # ACTION LISTENERS
    def browse_binary(self):
        filetypes = (
            ('Executable / Script', '*.exe;*.py'),
            ('All files', '*.*')
        ) if os.name == 'nt' else (
            ('All files', '*'),
        )
        
        filename = filedialog.askopenfilename(
            title="Locate compiled C++ Bot or Python Mock Script",
            initialdir=os.getcwd(),
            filetypes=filetypes
        )
        if filename:
            self.path_var.set(filename)

    def toggle_engine_connection(self):
        if self.engine.is_running:
            self.engine.stop()
            self.connection_status_lbl.config(text="🔴 DISCONNECTED", foreground="#f87171")
            self.btn_connect.config(text="Connect Engine")
        else:
            path = self.path_var.get()
            if not path or not os.path.exists(path):
                messagebox.showerror("Error", "Please select a valid compiled C++ UCI Chess Bot binary executable or python script.")
                return
            
            success = self.engine.start(path)
            if success:
                self.connection_status_lbl.config(text="🟢 CONNECTED (UCI)", foreground="#34d399")
                self.btn_connect.config(text="Disconnect")

    def send_uci_command(self, cmd):
        self.engine.send_command(cmd)

    def send_options(self):
        # Configure UCI performance parameters
        self.send_uci_command(f"setoption name Threads value {self.thread_spin.get()}")
        self.send_uci_command(f"setoption name Hash value {self.hash_spin.get()}")

    def reset_game(self):
        self.custom_moves = []
        self.board_state = [row[:] for row in DEFAULT_BOARD]
        self.lbl_moves.config(text="Moves sent: none")
        self.lbl_bestmove.config(text="💡 Best response: Pending engine request")
        self.current_fen = STARTING_FEN
        self.fen_var.set(self.current_fen)
        self.canvas.draw()
        if self.engine.is_running:
            self.engine.send_command("ucinewgame")
            self.engine.send_command("isready")

    def apply_fen_click(self):
        fen = self.fen_var.get().strip()
        if not fen:
            return
        
        success = self.parse_fen(fen)
        if success:
            self.current_fen = fen
            self.canvas.draw()
            self.custom_moves = []
            if self.engine.is_running:
                self.engine.send_command(f"position fen {fen}")
        else:
            messagebox.showerror("Parse Error", "Invalid FEN chess format entered.")

    def send_manual_cmd(self):
        cmd = self.cmd_var.get().strip()
        if cmd:
            self.send_uci_command(cmd)
            self.cmd_var.set("")

    # ENGINE EVENTS
    def on_engine_log(self, text, style_tag):
        self.log_text.insert(tk.END, text, style_tag)
        self.log_text.see(tk.END)

    def on_engine_info(self, info):
        # Parse score
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
                else: # mate
                    self.last_engine_eval = float(v)
                    self.last_score_mate = True
                    prefix = "+" if v >= 0 else "-"
                    self.lbl_eval_score.config(text=f"MATE in {prefix}{abs(v)}")
            except Exception:
                pass
            self.eval_canvas.draw()
            
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
                self.lbl_eval_nps.config(text=f"{nps_val:,} nps")
            except Exception:
                self.lbl_eval_nps.config(text=info["nps"])

    def on_bestmove(self, best, ponder):
        p_str = f" | Ponder: {ponder}" if ponder else ""
        self.lbl_bestmove.config(text=f"💡 Best move found: {best}{p_str}")

    def update_engine_queue(self):
        self.engine.update()
        self.after(50, self.update_engine_queue)


if __name__ == "__main__":
    app = ChessGUI()
    
    # Handle clean exit of child process if window is closed
    def on_close():
        app.engine.stop()
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()