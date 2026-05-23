import tkinter as tk
from tkinter import ttk

class UCIPanelRenderer:
    """
    Decoupled visual stylesheet and theme configurator for UCIPanel.
    Queries active theme properties and applies style parameters to widgets.
    Matches the pattern of BoardRenderer in the board folder.
    """
    def __init__(self, panel, theme):
        self.panel = panel
        self.theme = theme

    def update_theme(self, theme):
        """
        Updates the active theme reference.
        """
        self.theme = theme

    def setup_ttk_styles(self):
        """
        Defines TTK styles for panel cards, backgrounds, and standard labels.
        """
        style = ttk.Style()
        
        # Pull backgrounds and text colors from theme, with safe fallbacks
        bg_dark = getattr(self.theme, "WINDOW_BG", "#0f172a")
        bg_mid = getattr(self.theme, "CARD_BG", "#1e293b")
        fg = getattr(self.theme, "TEXT", "#f8fafc")
        accent = getattr(self.theme, "HIGHLIGHT", "#38bdf8")
        success = getattr(self.theme, "SUCCESS", "#34d399")
        danger = getattr(self.theme, "DANGER", "#f87171")

        style.configure("ControlPanel.TFrame", background=bg_dark)
        style.configure("Card.TFrame", background=bg_mid, relief="flat")
        
        style.configure("CardTitle.TLabel", background=bg_mid, foreground=accent, font=("Segoe UI", 9, "bold"))
        style.configure("CardText.TLabel", background=bg_mid, foreground=fg, font=("Segoe UI", 9))
        style.configure("CardMetric.TLabel", background=bg_mid, foreground=fg, font=("Consolas", 10, "bold"))
        
        style.configure("StatusDisconnected.TLabel", background=bg_mid, foreground=danger, font=("Segoe UI", 9, "bold"))
        style.configure("StatusConnected.TLabel", background=bg_mid, foreground=success, font=("Segoe UI", 9, "bold"))

    def apply_theme(self):
        """
        Directly injects background, foreground, border, active states,
        and log tagging color properties to Tkinter sub-components.
        """
        bg_dark = getattr(self.theme, "WINDOW_BG", "#0f172a")
        bg_input = getattr(self.theme, "INPUT_BG", "#090d16")
        fg = getattr(self.theme, "TEXT", "#f8fafc")
        accent = getattr(self.theme, "HIGHLIGHT", "#38bdf8")
        success = getattr(self.theme, "SUCCESS", "#34d399")
        danger = getattr(self.theme, "DANGER", "#f87171")
        warning = getattr(self.theme, "WARNING", "#fbbf24")

        # 1. Input entries (exec path & manual command input)
        for entry in [self.panel.path_entry, self.panel.cmd_entry]:
            if entry:
                entry.configure(
                    bg=bg_input,
                    fg=fg,
                    insertbackground=accent,
                    highlightthickness=1,
                    highlightbackground="#334155",
                    highlightcolor=accent
                )

        # 2. Spinboxes (threads, hash, depth, time)
        for spin in [self.panel.thread_spin, self.panel.hash_spin, self.panel.depth_spin, self.panel.time_spin]:
            if spin:
                spin.configure(
                    bg=bg_input,
                    fg=fg,
                    insertbackground=accent,
                    highlightthickness=1,
                    highlightbackground="#334155",
                    highlightcolor=accent
                )

        # 3. Text terminal log monitor
        if self.panel.log_text:
            self.panel.log_text.configure(
                bg=bg_input,
                fg=fg,
                highlightthickness=1,
                highlightbackground="#334155"
            )
            # Re-configure tag colors dynamically
            self.panel.log_text.tag_config("sent", foreground=accent)
            self.panel.log_text.tag_config("received", foreground="#cbd5e1")
            self.panel.log_text.tag_config("error", foreground=danger)
            self.panel.log_text.tag_config("warning", foreground=warning)

        # 4. Standard buttons
        standard_buttons = [
            (self.panel.btn_browse, "#334155", "#475569", fg, fg),
            (self.panel.btn_ready, "#475569", "#64748b", fg, fg),
            (self.panel.btn_reset, "#475569", "#64748b", fg, fg),
            (self.panel.btn_send_options, "#334155", "#475569", fg, fg),
            (self.panel.btn_go_depth, accent, "#7dd3fc", bg_dark, bg_dark),
            (self.panel.btn_go_time, accent, "#7dd3fc", bg_dark, bg_dark),
            (self.panel.btn_send, accent, "#7dd3fc", bg_dark, bg_dark),
        ]
        for btn, bg, abg, btn_fg, afg in standard_buttons:
            if btn:
                btn.configure(
                    bg=bg,
                    fg=btn_fg,
                    activebackground=abg,
                    activeforeground=afg
                )

        # 5. Core action buttons with alerts (Infinite, Halt/Stop)
        if self.panel.btn_inf:
            self.panel.btn_inf.configure(
                bg=success,
                fg=bg_dark,
                activebackground="#6ee7b7",
                activeforeground=bg_dark
            )
        if self.panel.btn_halt:
            self.panel.btn_halt.configure(
                bg=danger,
                fg=bg_dark,
                activebackground="#fda4af",
                activeforeground=bg_dark
            )

        # 6. Dynamic Connection Connect Button
        self.apply_connection_style()

    def apply_connection_style(self):
        """
        Dynamically applies connection state specific styles to the connect button.
        """
        if not self.panel.btn_connect:
            return

        bg_dark = getattr(self.theme, "WINDOW_BG", "#0f172a")
        accent = getattr(self.theme, "HIGHLIGHT", "#38bdf8")
        danger = getattr(self.theme, "DANGER", "#f87171")

        if self.panel.engine and self.panel.engine.is_running:
            self.panel.btn_connect.configure(
                bg=danger,
                fg=bg_dark,
                activebackground="#fda4af",
                activeforeground=bg_dark
            )
        else:
            self.panel.btn_connect.configure(
                bg=accent,
                fg=bg_dark,
                activebackground="#7dd3fc",
                activeforeground=bg_dark
            )
