# gui/views/dashboard_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from gui.themes.theme_manager import theme_manager

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # 1. Header Banner Block
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"QFrame {{ background-color: rgba(22, 17, 38, 0.5); border: 1px solid rgba(0, 229, 255, 0.15); border-radius: 8px; }}"
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(20)

        # Welcome texts
        text_layout = QVBoxLayout()
        title_lbl = QLabel("WELCOME TO BLUIE CHESS WORKBENCH")
        title_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 20px; font-weight: bold; color: {self.theme.console_in.name()};")
        desc_lbl = QLabel("A high-performance C++ chess engine development, testing, and play dashboard.")
        desc_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; color: {self.theme.panel_text.name()};")
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(desc_lbl)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        layout.addWidget(header_frame)

        # 2. Main content splits (Launch Center vs Stats cards)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # Launch Card
        launch_card = QFrame()
        launch_card.setStyleSheet(
            f"QFrame {{ background-color: rgba(22, 17, 38, 0.3); border: 1px solid {self.theme.panel_border.name()}; border-radius: 6px; }}"
        )
        launch_layout = QVBoxLayout(launch_card)
        launch_layout.setContentsMargins(20, 20, 20, 20)
        launch_layout.setSpacing(15)

        launch_title = QLabel("Launch Game Center")
        launch_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 15px; font-weight: bold; color: {self.theme.console_in.name()};")
        launch_layout.addWidget(launch_title)

        play_btn = QPushButton("Play vs C++ Engine")
        play_btn.setStyleSheet(
            f"QPushButton {{ background-color: {self.theme.dark_square.name()}; color: #FFFFFF; font-family: 'Outfit'; font-weight: bold; border-radius: 4px; padding: 10px; border: none; }}"
            f"QPushButton:hover {{ background-color: {self.theme.light_square.name()}; color: {self.theme.dark_square.name()}; }}"
        )
        launch_layout.addWidget(play_btn)

        analysis_btn = QPushButton("Start Free Position Analysis")
        analysis_btn.setStyleSheet(
            f"QPushButton {{ background-color: transparent; color: {self.theme.console_out.name()}; font-family: 'Outfit'; border-radius: 4px; padding: 10px; border: 1px solid {self.theme.console_out.name()}; }}"
            f"QPushButton:hover {{ background-color: rgba(224, 64, 251, 0.1); }}"
        )
        launch_layout.addWidget(analysis_btn)
        launch_layout.addStretch()

        # Stats Card
        stats_card = QFrame()
        stats_card.setStyleSheet(
            f"QFrame {{ background-color: rgba(22, 17, 38, 0.3); border: 1px solid {self.theme.panel_border.name()}; border-radius: 6px; }}"
        )
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(15)

        stats_title = QLabel("Telemetry Overview")
        stats_title.setStyleSheet(f"font-family: 'Outfit'; font-size: 15px; font-weight: bold; color: {self.theme.console_in.name()};")
        stats_layout.addWidget(stats_title)

        # Quick stats labels
        engine_speed = QLabel("Avg Search Speed: 5.3M NPS")
        engine_speed.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; color: {self.theme.panel_text.name()};")
        stats_layout.addWidget(engine_speed)

        engine_build = QLabel("Engine Target: C++20 Ninja x64")
        engine_build.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; color: {self.theme.panel_text.name()};")
        stats_layout.addWidget(engine_build)

        stats_layout.addStretch()

        main_layout.addWidget(launch_card, 3)
        main_layout.addWidget(stats_card, 2)

        layout.addLayout(main_layout)
        layout.addStretch()

    def update_theme(self) -> None:
        """Reactive theme updating."""
        self.theme = theme_manager.get_theme()
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")
