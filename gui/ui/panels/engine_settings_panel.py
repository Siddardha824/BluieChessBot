"""
Engine settings panel UI component.

This module provides the EngineSettingsPanel view, allowing the user to configure
the UCI chess engine executable path and search limits (depth, time, or node constraints).
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QGroupBox, QFormLayout, QComboBox, 
    QSpinBox, QLineEdit, QFileDialog, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QFontMetrics
from gui.ui.core import StyledWidget


class EngineSettingsPanel(StyledWidget):
    """
    UI widget for modifying UCI chess engine search and executable settings.

    This panel displays inputs for selecting the engine binary file and configuring
    search depth, node limits, or search time. Updates are emitted as an intent
    signal to be handled by the MVVM coordinator.

    Signals:
        engine_settings_changed (Signal): Emitted when the user saves updated settings.
            Payload: settings (dict) with keys 'constraint_mode', 'constraint_value', 'engine_path'.

    Styling:
        Relies on the `#engineSettingsPanel` ID for QSS styling selector.
    """
    
    # Emitted when the user successfully saves settings. Payload: settings (dict)
    engine_settings_changed = Signal(dict)

    # --- UI Initialization ---

    def __init__(self, parent):
        """Initialize the engine settings panel.

        Args:
            parent: The parent QWidget.
        """
        super().__init__(object_name="engineSettingsPanel", parent=parent)

    def _setup_ui(self):
        """Set up the layout, groups, and inputs for settings configuration."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Engine Executable ---
        path_group = QGroupBox("Engine Executable")
        path_layout = QVBoxLayout(path_group)
        
        engine_layout = QHBoxLayout()
        self.engine_path_edit = QLineEdit()
        self.engine_path_edit.setPlaceholderText("Path to engine executable...")
        self.engine_browse_btn = QPushButton("...")
        self.engine_browse_btn.setFixedWidth(40)
        
        engine_layout.addWidget(self.engine_path_edit)
        engine_layout.addWidget(self.engine_browse_btn)

        path_layout.addLayout(engine_layout)

        # --- Search Limits ---
        limits_group = QGroupBox("Search Limits")
        limits_layout = QFormLayout(limits_group)

        self.constraint_combo = QComboBox()
        self.constraint_combo.addItems(["Depth", "Time (ms)", "Nodes (kN)"])
        
        self.constraint_spinbox = QSpinBox()
        self.constraint_spinbox.setRange(1, 10000000)
        self.constraint_spinbox.setValue(20)

        limits_layout.addRow("Limit Type:", self.constraint_combo)
        limits_layout.addRow("Value:", self.constraint_spinbox)

        self.save_btn = QPushButton("Save")

        layout.addWidget(path_group)
        layout.addWidget(limits_group)
        layout.addWidget(self.save_btn)
        layout.addStretch()

        self._connect_signals()

    def _connect_signals(self):
        """Connect UI interactive triggers to corresponding slot handlers."""
        self.engine_browse_btn.clicked.connect(self._browse_for_engine)
        self.save_btn.clicked.connect(self._save_settings)

    # --- Private Slots (User Intents) ---

    def _browse_for_engine(self):
        """Open a file dialog for the user to select the engine executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Chess Engine", "", "Executables (*.exe *.bin);;All Files (*)"
        )
        if file_path:
            metrics = QFontMetrics(self.engine_path_edit.font())
            
            available_width = self.engine_path_edit.width() - 10
            
            # Elide middle of path if it exceeds the visible edit box width
            elided_path = metrics.elidedText(
                file_path, 
                Qt.TextElideMode.ElideMiddle, 
                available_width
            )
            
            self.engine_path_edit.setText(elided_path)
            self.engine_path_edit.setToolTip(file_path)

    def _save_settings(self):
        """Collect input states and emit the engine_settings_changed signal."""
        settings = {
            "constraint_mode": self.constraint_combo.currentText(),
            "constraint_value": self.constraint_spinbox.value(),
            "engine_path": self.engine_path_edit.toolTip()
        }

        self.engine_settings_changed.emit(settings)

    # --- Public Slots (State Updates) ---

    def set_initial_values(self, constraint_type: str, constraint_value: int, engine_path: str):
        """Populate inputs with current settings values without emitting change signals.

        Args:
            constraint_type: Active constraint selector string (e.g. 'Depth').
            constraint_value: Positive integer constraint value.
            engine_path: Physical filesystem path to the UCI engine executable.
        """
        self.blockSignals(True)
        self.constraint_combo.setCurrentText(constraint_type)
        self.constraint_spinbox.setValue(constraint_value)
        self.engine_path_edit.setText(engine_path)
        self.engine_path_edit.setToolTip(engine_path)
        self.blockSignals(False)