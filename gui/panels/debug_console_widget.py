# gui/panels/debug_console_widget.py

from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from datetime import datetime
from typing import Optional

class DebugConsoleWidget(QWidget):
    def __init__(self, theme=None, parent=None):
        """
        Initializes the scrollable UCI / Debug Console.
        Provides a beautifully formatted log interface, fully synchronized with current active themes.
        """
        super().__init__(parent)
        from gui.themes.default_theme import DefaultTheme
        self.theme = theme if theme is not None else DefaultTheme()
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Load panel colors dynamically from theme to enforce zero hardcoded values
        bg_hex = self.theme.panel_background.name()
        text_hex = self.theme.panel_text.name()
        border_hex = self.theme.panel_border.name()
        
        self.text_area.setStyleSheet(
            f"QTextEdit {{ background-color: {bg_hex}; color: {text_hex}; border: 1px solid {border_hex}; font-family: Consolas; font-size: 11px; }}"
        )
        
        # Add a sleek "Clear Logs" trigger button styled dynamically
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Console")
        clear_btn.setStyleSheet(
            f"QPushButton {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; "
            f"border: 1px solid {self.theme.panel_text_muted.name()}; padding: 4px 8px; border-radius: 3px; }}"
            f"QPushButton:hover {{ background-color: {self.theme.panel_text_muted.name()}; color: {self.theme.panel_background.name()}; }}"
        )
        clear_btn.clicked.connect(self.text_area.clear)
        button_layout.addStretch()
        button_layout.addWidget(clear_btn)
        
        layout.addWidget(self.text_area)
        layout.addLayout(button_layout)

    def log_message(self, category: str, message: str) -> None:
        """
        Formats and appends a categorized log to the text log console.
        Categories: 'UCI_IN', 'UCI_OUT', 'INFO', 'ERROR'
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Pull category highlight color names dynamically from theme!
        color_map = {
            'UCI_IN': self.theme.console_in.name(),
            'UCI_OUT': self.theme.console_out.name(),
            'INFO': self.theme.console_info.name(),
            'ERROR': self.theme.console_error.name()
        }
        color = color_map.get(category, self.theme.panel_text.name())
        muted_color = self.theme.panel_text_muted.name()
        
        formatted_msg = f'<font color="{muted_color}">[{timestamp}]</font> ' \
                        f'<font color="{color}"><b>[{category}]</b></font> {message}'
                        
        self.text_area.append(formatted_msg)
        
        # Smooth scroll to ensure the latest logs are always visible
        self.text_area.moveCursor(self.text_area.textCursor().MoveOperation.End)
