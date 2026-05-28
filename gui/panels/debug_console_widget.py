# gui/panels/debug_console_widget.py

from PySide6.QtWidgets import (
    QWidget, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout,
    QLineEdit, QComboBox, QLabel
)
from PySide6.QtCore import Qt
from datetime import datetime
from typing import Optional

class DebugConsoleWidget(QWidget):
    def __init__(self, theme=None, engine_manager=None, parent=None):
        """
        Initializes the scrollable UCI / Debug Console with a sleek, dynamic command panel.
        Provides a beautifully formatted log interface, fully synchronized with active themes.
        """
        super().__init__(parent)
        self.engine_manager = engine_manager
        from gui.themes import theme_manager
        self.theme = theme if theme is not None else theme_manager.get_theme()
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
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
        
        # Create control layout for debug commands input and selection
        control_layout = QHBoxLayout()
        control_layout.setSpacing(6)
        
        cmd_label = QLabel("Command:")
        cmd_label.setStyleSheet(
            f"QLabel {{ color: {self.theme.panel_text.name()}; font-family: '{self.theme.font_family}'; font-size: 11px; font-weight: bold; }}"
        )
        
        # Dropdown (ComboBox) for debug commands
        self.cmd_dropdown = QComboBox()
        self.cmd_dropdown.setStyleSheet(
            f"QComboBox {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; "
            f"border: 1px solid {self.theme.panel_border.name()}; border-radius: 3px; padding: 3px 20px 3px 6px; font-family: '{self.theme.font_family}'; font-size: 11px; }}"
            f"QComboBox QAbstractItemView {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; selection-background-color: {self.theme.panel_border.name()}; }}"
        )
        
        debug_commands = [
            "-- Quick Select --",
            "isready",
            "bluie-debug board",
            "bluie-debug bitboards",
            "bluie-debug validate",
            "bluie-debug runtests",
            "bluie-debug legalmoves",
            "bluie-debug attacks white",
            "bluie-debug attacks black",
            "bluie-debug attacksto e3 white",
            "bluie-debug attacksto d5 black",
            "position startpos",
            "go depth 5"
        ]
        self.cmd_dropdown.addItems(debug_commands)
        self.cmd_dropdown.currentIndexChanged.connect(self._handle_dropdown_changed)
        
        # Input QLineEdit for typing and modification
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter raw UCI command or modify dropdown option...")
        self.cmd_input.setStyleSheet(
            f"QLineEdit {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; "
            f"border: 1px solid {self.theme.panel_border.name()}; border-radius: 3px; padding: 4px 8px; font-family: Consolas; font-size: 11px; }}"
            f"QLineEdit:focus {{ border: 1px solid {self.theme.panel_text_muted.name()}; }}"
        )
        self.cmd_input.returnPressed.connect(self.send_manually)
        
        # Send Trigger
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet(
            f"QPushButton {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; "
            f"border: 1px solid {self.theme.panel_text_muted.name()}; padding: 4px 12px; border-radius: 3px; font-family: '{self.theme.font_family}'; font-weight: bold; font-size: 11px; }}"
            f"QPushButton:hover {{ background-color: {self.theme.panel_text_muted.name()}; color: {self.theme.panel_background.name()}; }}"
        )
        self.send_btn.clicked.connect(self.send_manually)
        
        # Clear Logs trigger button styled dynamically
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(
            f"QPushButton {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; "
            f"border: 1px solid {self.theme.panel_text_muted.name()}; padding: 4px 12px; border-radius: 3px; font-family: '{self.theme.font_family}'; font-size: 11px; }}"
            f"QPushButton:hover {{ background-color: {self.theme.panel_text_muted.name()}; color: {self.theme.panel_background.name()}; }}"
        )
        clear_btn.clicked.connect(self.text_area.clear)
        
        control_layout.addWidget(cmd_label)
        control_layout.addWidget(self.cmd_dropdown, stretch=1)
        control_layout.addWidget(self.cmd_input, stretch=3)
        control_layout.addWidget(self.send_btn)
        control_layout.addWidget(clear_btn)
        
        layout.addWidget(self.text_area)
        layout.addLayout(control_layout)

    def _handle_dropdown_changed(self, index: int) -> None:
        """Populates the input line edit with the selected dropdown command."""
        if index > 0:
            cmd = self.cmd_dropdown.itemText(index)
            self.cmd_input.setText(cmd)
            self.cmd_input.setFocus()

    def send_manually(self) -> None:
        """Sends the command in the line edit directly to the active C++ engine."""
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
            
        if self.engine_manager:
            self.engine_manager.send_command(cmd)
            self.cmd_input.clear()
            self.cmd_dropdown.setCurrentIndex(0)
        else:
            self.log_message("ERROR", "Cannot send command: engine is disconnected or not initialized.")

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

    def update_theme(self, theme) -> None:
        """Dynamically redraws the log stylesheet when themes change."""
        self.theme = theme
        bg_hex = self.theme.panel_background.name()
        text_hex = self.theme.panel_text.name()
        border_hex = self.theme.panel_border.name()
        self.text_area.setStyleSheet(
            f"QTextEdit {{ background-color: {bg_hex}; color: {text_hex}; border: 1px solid {border_hex}; font-family: Consolas; font-size: 11px; }}"
        )
