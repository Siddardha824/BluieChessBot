"""
Global settings panel UI component.

This module provides the GlobalSettingsPanel view, allowing the user to configure
global preferences such as the UI theme and PGN save directory.
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QVBoxLayout, QGroupBox, QFormLayout, QComboBox, 
    QLineEdit, QFileDialog, QPushButton, QHBoxLayout
)
from gui.ui.core import StyledWidget


class GlobalSettingsPanel(StyledWidget):
    """
    UI widget for modifying application-wide configuration settings.

    This panel displays inputs for selecting the visual theme from a list of presets
    and choosing the default directory for saving PGN files. Updates are emitted
    as an intent signal to be handled by the MVVM coordinator.

    Signals:
        global_settings_changed (Signal): Emitted when the user saves updated settings.
            Payload: settings (dict) with keys 'theme_name', 'game_save_path'.

    Styling:
        Relies on the `#settingsPanel` ID for QSS styling selector.
    """

    # Emitted when the user successfully saves settings. Payload: settings (dict)
    global_settings_changed = Signal(dict)

    # --- UI Initialization ---

    def __init__(self, parent):
        """Initialize the global settings panel.

        Args:
            parent: The parent QWidget.
        """
        super().__init__(object_name="settingsPanel", parent=parent)
        self._connect_signals()

    def _setup_ui(self):
        """Set up the layout, groups, and inputs for global settings."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(15)

        prefs_group = QGroupBox("App Preferences")
        prefs_group.setObjectName("prefsGroup")
        prefs_layout = QFormLayout(prefs_group)

        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("themeCombo")
        self.theme_combo.addItems([])

        pgn_layout = QHBoxLayout()
        self.pgn_path_edit = QLineEdit()
        self.pgn_path_edit.setObjectName("pgnPathEdit")
        self.pgn_path_edit.setPlaceholderText("Directory to save PGN game...")
        
        self.browse_btn = QPushButton("...")
        self.browse_btn.setObjectName("pgnBrowseBtn")
        self.browse_btn.setFixedWidth(40)
        
        pgn_layout.addWidget(self.pgn_path_edit)
        pgn_layout.addWidget(self.browse_btn)

        self.save_btn = QPushButton("Save")

        prefs_layout.addRow("Theme:", self.theme_combo)
        prefs_layout.addRow("PGN Save Folder:", pgn_layout)
        self._layout.addWidget(prefs_group)
        self._layout.addWidget(self.save_btn)

        self._layout.addStretch()

    def _connect_signals(self):
        """Connect UI interactive triggers to corresponding slot handlers."""
        self.browse_btn.clicked.connect(self._browse_for_pgn_dir)
        self.save_btn.clicked.connect(self._save_settings)

    # --- Private Slots (User Intents) ---

    def _browse_for_pgn_dir(self):
        """Open a directory selection dialog to set the PGN save location."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select PGN Save Directory", f"{self.pgn_path_edit.text()}", QFileDialog.Option.ShowDirsOnly
        )
        if dir_path:
            metrics = QFontMetrics(self.pgn_path_edit.font())
                        
            available_width = self.pgn_path_edit.width() - 10
            
            # Elide middle of path if it exceeds the visible edit box width
            elided_path = metrics.elidedText(
                dir_path, 
                Qt.TextElideMode.ElideMiddle, 
                available_width
            )
            
            self.pgn_path_edit.setText(elided_path)
            self.pgn_path_edit.setToolTip(dir_path)

    def _save_settings(self):
        """Collect input states and emit the global_settings_changed signal."""
        settings = {
            "theme_name": self.theme_combo.currentText(),
            "game_save_path": self.pgn_path_edit.toolTip()
        }

        self.global_settings_changed.emit(settings)

    # --- Public Slots (State Updates) ---

    def set_available_themes(self, themes: list[str], current_theme: str):
        """Populate the theme dropdown and set the current active selection.

        Args:
            themes: A list of available theme names.
            current_theme: The theme name to select by default.
        """
        self.theme_combo.clear()
        self.theme_combo.addItems(themes)
        self.theme_combo.setCurrentText(current_theme)

    def set_initial_values(self, themes: list[str], current_theme: str, pgn_save_path: str):
        """Populate the panel inputs with initial settings values.

        Args:
            themes: A list of available theme names.
            current_theme: The active theme name.
            pgn_save_path: Directory path where PGN games are saved.
        """
        self.blockSignals(True)
        self.set_available_themes(themes, current_theme)
        self.pgn_path_edit.setText(pgn_save_path)
        self.pgn_path_edit.setToolTip(pgn_save_path)
        self.blockSignals(False)