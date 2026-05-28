# gui/views/dashboard_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QComboBox, QSlider, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from gui.themes.theme_manager import theme_manager
from gui.core.app_state import app_state

class DashboardView(QWidget):
    def __init__(self, parent=None):
        """
        Initializes the dynamic, beautifully styled Chess Workbench Dashboard.
        Integrates dynamic configuration selectors, parameter sliders, and persistent stats metrics.
        """
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self._init_ui()
        self.refresh_stats()

        # Connect to state change signals to ensure reactive visual refreshes
        app_state.signals.theme_changed.connect(lambda: self.update_theme())

    def _init_ui(self) -> None:
        # Parent layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(25)
        
        # Apply parent background matching active themes
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")

        # ==========================================
        # 1. PREMIUM HEADER BANNER
        # ==========================================
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 25, 25, 25)
        header_layout.setSpacing(10)
        
        title_lbl = QLabel("BLUIE CHESS TELEMETRY WORKBENCH")
        title_lbl.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 24px; font-weight: 800; "
            f"color: {self.theme.console_in.name()};"
        )
        desc_lbl = QLabel(
            "State-of-the-art C++ chess engine compiler, hardware-scaling benchmark suite, "
            "and legal moves debugger."
        )
        desc_lbl.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 13px; font-weight: 500; "
            f"color: {self.theme.panel_text.name()};"
        )
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(desc_lbl)
        layout.addWidget(header_frame)

        # ==========================================
        # 2. MAIN LAYOUT SPLITS
        # ==========================================
        main_layout = QHBoxLayout()
        main_layout.setSpacing(25)

        # ------------------------------------------
        # A. LEFT SIDE: GAME COMPILER & PLAY CENTER
        # ------------------------------------------
        play_card = QFrame()
        play_card.setObjectName("PlayCard")
        play_layout = QVBoxLayout(play_card)
        play_layout.setContentsMargins(25, 25, 25, 25)
        play_layout.setSpacing(20)

        play_title = QLabel("LAUNCH CENTER")
        play_title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 16px; font-weight: 700; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        play_layout.addWidget(play_title)

        # Game Mode Form
        mode_lbl = QLabel("Game Mode")
        mode_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.panel_text_muted.name()}; text-transform: uppercase;")
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Human vs Engine",
            "Engine vs Engine (Spectator)",
            "Free Play / Analysis",
            "Two-Player Local"
        ])
        play_layout.addWidget(mode_lbl)
        play_layout.addWidget(self.mode_selector)

        # Engine Depth Slider Row
        depth_lbl_layout = QHBoxLayout()
        depth_title = QLabel("Engine Search Depth")
        depth_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.panel_text_muted.name()}; text-transform: uppercase;")
        self.depth_val = QLabel("6")
        self.depth_val.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: {self.theme.console_in.name()};")
        depth_lbl_layout.addWidget(depth_title)
        depth_lbl_layout.addStretch()
        depth_lbl_layout.addWidget(self.depth_val)
        
        self.depth_slider = QSlider(Qt.Orientation.Horizontal)
        self.depth_slider.setRange(1, 20)
        self.depth_slider.setValue(6)
        self.depth_slider.valueChanged.connect(lambda val: self.depth_val.setText(str(val)))
        
        play_layout.addLayout(depth_lbl_layout)
        play_layout.addWidget(self.depth_slider)

        # Time Overhead / Search Limit Row
        time_lbl_layout = QHBoxLayout()
        time_title = QLabel("Search Time Limit")
        time_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.panel_text_muted.name()}; text-transform: uppercase;")
        self.time_val = QLabel("Infinite")
        self.time_val.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: {self.theme.console_in.name()};")
        time_lbl_layout.addWidget(time_title)
        time_lbl_layout.addStretch()
        time_lbl_layout.addWidget(self.time_val)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 30)  # 0 represents Infinite
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self._handle_time_slider)

        play_layout.addLayout(time_lbl_layout)
        play_layout.addWidget(self.time_slider)

        # Action Buttons
        play_layout.addSpacing(10)
        self.start_btn = QPushButton("START MATCH WORKSPACE")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._handle_match_start)
        play_layout.addWidget(self.start_btn)
        play_layout.addStretch()

        # ------------------------------------------
        # B. RIGHT SIDE: TELEMETRY & RUNTIME ANALYTICS
        # ------------------------------------------
        stats_card = QFrame()
        stats_card.setObjectName("StatsCard")
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(25, 25, 25, 25)
        stats_layout.setSpacing(20)

        stats_title = QLabel("TELEMETRY STATS")
        stats_title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 16px; font-weight: 700; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        stats_layout.addWidget(stats_title)

        # Stats Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: transparent; border: none;")
        grid = QGridLayout(grid_frame)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(15)

        # Metric 1: Lifetime Moves
        moves_block = QFrame()
        moves_block.setObjectName("MetricBlock")
        mb_layout = QVBoxLayout(moves_block)
        mb_layout.setContentsMargins(15, 15, 15, 15)
        mb_layout.setSpacing(5)
        mb_title = QLabel("CALCULATED MOVES")
        mb_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 9px; font-weight: bold; color: {self.theme.panel_text_muted.name()};")
        self.mb_value = QLabel("0")
        self.mb_value.setStyleSheet(f"font-family: 'Outfit'; font-size: 22px; font-weight: 800; color: {self.theme.console_in.name()};")
        mb_layout.addWidget(mb_title)
        mb_layout.addWidget(self.mb_value)
        grid.addWidget(moves_block, 0, 0)

        # Metric 2: Average NPS
        nps_block = QFrame()
        nps_block.setObjectName("MetricBlock")
        nb_layout = QVBoxLayout(nps_block)
        nb_layout.setContentsMargins(15, 15, 15, 15)
        nb_layout.setSpacing(5)
        nb_title = QLabel("AVERAGE SPEED")
        nb_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 9px; font-weight: bold; color: {self.theme.panel_text_muted.name()};")
        self.nb_value = QLabel("0.0M NPS")
        self.nb_value.setStyleSheet(f"font-family: 'Outfit'; font-size: 22px; font-weight: 800; color: {self.theme.console_in.name()};")
        nb_layout.addWidget(nb_title)
        nb_layout.addWidget(self.nb_value)
        grid.addWidget(nps_block, 0, 1)

        # Metric 3: Wins
        wins_block = QFrame()
        wins_block.setObjectName("MetricBlock")
        wb_layout = QVBoxLayout(wins_block)
        wb_layout.setContentsMargins(15, 15, 15, 15)
        wb_layout.setSpacing(5)
        wb_title = QLabel("MATCH VICTORIES")
        wb_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 9px; font-weight: bold; color: {self.theme.panel_text_muted.name()};")
        self.wb_value = QLabel("0")
        self.wb_value.setStyleSheet(f"font-family: 'Outfit'; font-size: 22px; font-weight: 800; color: #B2FF59;")
        wb_layout.addWidget(wb_title)
        wb_layout.addWidget(self.wb_value)
        grid.addWidget(wins_block, 1, 0)

        # Metric 4: Loss/Draw
        losses_block = QFrame()
        losses_block.setObjectName("MetricBlock")
        lb_layout = QVBoxLayout(losses_block)
        lb_layout.setContentsMargins(15, 15, 15, 15)
        lb_layout.setSpacing(5)
        lb_title = QLabel("DEFEATS / DRAWS")
        lb_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 9px; font-weight: bold; color: {self.theme.panel_text_muted.name()};")
        self.lb_value = QLabel("0 / 0")
        self.lb_value.setStyleSheet(f"font-family: 'Outfit'; font-size: 20px; font-weight: 800; color: {self.theme.panel_text.name()};")
        lb_layout.addWidget(lb_title)
        lb_layout.addWidget(self.lb_value)
        grid.addWidget(losses_block, 1, 1)

        stats_layout.addWidget(grid_frame)
        stats_layout.addStretch()

        main_layout.addWidget(play_card, 3)
        main_layout.addWidget(stats_card, 2)
        layout.addLayout(main_layout)
        
        self.update_stylesheets()

    def _handle_time_slider(self, val: int) -> None:
        if val == 0:
            self.time_val.setText("Infinite")
        else:
            self.time_val.setText(f"{val}s")

    def _handle_match_start(self) -> None:
        """Saves current match options and routes to the Analysis View."""
        depth = self.depth_slider.value()
        time_limit = self.time_slider.value()
        mode = self.mode_selector.currentText()

        # Update engine settings inside AppState
        app_state.update_engine_options({
            "Depth": depth,
            "TimeLimit": time_limit,
            "GameMode": mode
        })

        # Transition stack to Chessboard Analysis view
        app_state.active_page = "ANALYSIS"

    def refresh_stats(self) -> None:
        """Refreshes the telemetry dashboard layout from loaded app_state profile metrics."""
        stats = app_state.stats
        self.mb_value.setText(f"{stats.get('total_moves', 0):,}")
        self.nb_value.setText(f"{stats.get('avg_nps', 0.0):.1f}M NPS")
        self.wb_value.setText(str(stats.get('wins', 0)))
        
        losses = stats.get('losses', 0)
        draws = stats.get('draws', 0)
        self.lb_value.setText(f"{losses} / {draws}")

    def update_stylesheets(self) -> None:
        bg_hex = self.theme.panel_background.name()
        border_hex = self.theme.panel_border.name()
        text_hex = self.theme.panel_text.name()
        text_muted = self.theme.panel_text_muted.name()
        glow_color = self.theme.console_in.name()
        button_bg = self.theme.dark_square.name()
        button_hover = self.theme.light_square.name()

        # High fidelity QSS stylesheet updates dynamically
        self.setStyleSheet(
            f"QWidget {{ background-color: {bg_hex}; }}"
            f"QFrame#HeaderFrame {{"
            f"  background-color: rgba(22, 17, 38, 0.4);"
            f"  border: 1px solid rgba(0, 229, 255, 0.12);"
            f"  border-radius: 8px;"
            f"}}"
            f"QFrame#PlayCard, QFrame#StatsCard {{"
            f"  background-color: rgba(22, 17, 38, 0.25);"
            f"  border: 1px solid {border_hex};"
            f"  border-radius: 6px;"
            f"}}"
            f"QFrame#MetricBlock {{"
            f"  background-color: rgba(255, 255, 255, 0.03);"
            f"  border: 1px solid rgba(255, 255, 255, 0.05);"
            f"  border-radius: 6px;"
            f"}}"
            f"QComboBox {{"
            f"  background-color: rgba(0, 0, 0, 0.3);"
            f"  color: {text_hex};"
            f"  border: 1px solid {border_hex};"
            f"  border-radius: 4px;"
            f"  padding: 8px;"
            f"  font-family: 'Outfit';"
            f"  font-size: 12px;"
            f"}}"
            f"QComboBox::drop-down {{"
            f"  border: none;"
            f"  subcontrol-origin: padding;"
            f"  subcontrol-position: top right;"
            f"  width: 15px;"
            f"}}"
            f"QSlider::groove:horizontal {{"
            f"  height: 5px;"
            f"  background: rgba(255, 255, 255, 0.08);"
            f"  border-radius: 2px;"
            f"}}"
            f"QSlider::handle:horizontal {{"
            f"  background: {glow_color};"
            f"  width: 14px;"
            f"  margin: -5px 0;"
            f"  border-radius: 7px;"
            f"}}"
            f"QPushButton {{"
            f"  background-color: {button_bg};"
            f"  color: #FFFFFF;"
            f"  border: none;"
            f"  border-radius: 4px;"
            f"  padding: 12px;"
            f"  font-family: 'Outfit';"
            f"  font-size: 13px;"
            f"  font-weight: bold;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {button_hover};"
            f"  color: {button_bg};"
            f"}}"
        )

    def update_theme(self) -> None:
        """Reactive theme updating."""
        self.theme = theme_manager.get_theme()
        self.update_stylesheets()
        self.refresh_stats()
