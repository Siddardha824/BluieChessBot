"""
UI component sandbox for previewing and testing decoupled panels.

This module provides a standalone PanelPreviewWindow class that serves as a
harness for rendering UI panels in isolation, testing their layout constraints,
and verifying theme customization capabilities.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt

from gui.app.theme.services.theme_service import ThemeService
from gui.ui.panels import (
    EngineAnalysisPanel,
    SingleEngineStatus,
    EnginesStatusPanel,
    EngineSettingsPanel,
    GlobalSettingsPanel,
    GameControlPanel,
    MoveHistoryPanel
)


class PanelPreviewWindow(QMainWindow):
    """
    Sandbox window for previewing decoupled UI components in isolation.

    This window acts as a component harness to load, display, and swap various
    UI panels (such as settings, engine status, and analysis panels) to verify
    their visual correctness, alignment, and dynamic stylesheet updates.

    Attributes:
        theme_service (ThemeService): Service managing application stylesheets and theme changes.
        panels (dict): Registry of previewable panels mapped to their class types and instantiation arguments.
        preview_container (QFrame): Layout container wrapping the currently loaded panel.
        panel_selector (QComboBox): Dropdown menu controlling which panel is active.
    """

    # --- UI Initialization ---

    def __init__(self):
        """Initialize the preview window and register previewable components."""
        super().__init__()
        self.setWindowTitle("Bluie UI Component Sandbox")
        self.resize(900, 600)
        
        self.theme_service = ThemeService()
        
        self.panels = {
            "Engine Analysis Panel": [EngineAnalysisPanel, {"parent": None}, (300, 500)],
            "Single Engine Status Panel": [SingleEngineStatus, {"engine_role": "Test", "parent": None}, (350, 150)],
            "Engine Status Panel": [EnginesStatusPanel, {"parent": None}, (350, 300)],
            "Engine Settings Panel": [EngineSettingsPanel, {"parent": None}, (400, 500)],
            "Global Settings Panel": [GlobalSettingsPanel, {"parent": None}, (400, 500)],
            "Game Control Panel":[GameControlPanel, {"parent": None}, (350, 300)],
            "Move History Panel": [MoveHistoryPanel, {"parent": None}, (300, 300)]
        }
        
        self._setup_ui()
        self._apply_default_theme()

    # --- Layout Setup ---

    def _setup_ui(self):
        """Build and configure the sandbox user interface layout."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Configure the control toolbar with panel selectors and theme toggles
        toolbar_layout = QHBoxLayout()
        
        self.panel_selector = QComboBox()
        self.panel_selector.addItems(list(self.panels.keys()))
        self.panel_selector.currentTextChanged.connect(self._load_panel)
        
        self.theme_button = QPushButton("Toggle Theme (Space/Default)")
        self.theme_button.clicked.connect(self._toggle_theme)
        
        toolbar_layout.addWidget(QLabel("Select Panel:"))
        toolbar_layout.addWidget(self.panel_selector)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.theme_button)
        
        # Configure the preview container
        # Use a QFrame to visually bound the component being tested
        self.preview_container = QFrame()
        self.preview_container.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_layout = QVBoxLayout(self.preview_container)
        
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.preview_container, stretch=1)
        
        # Load the initial panel
        self._load_panel(self.panel_selector.currentText())

    # --- Private Slots (User Intents) ---

    def _load_panel(self, panel_name: str):
        """Instantiate and display the selected panel in the preview container.

        This method clears any previously loaded widgets from the layout,
        instantiates the selected panel class with the predefined configuration,
        and adds it to the preview container layout.

        Args:
            panel_name: The name of the panel to load, matching a key in self.panels.
        """
        # Clear any existing panel widgets from the layout to avoid overlap
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            widget = None
            if item:
                widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # Instantiate the UI component with parent=None to test isolation constraints
        panel = self.panels.get(panel_name)
        if panel:
            panel_class = panel[0]
            active_panel = panel_class(**panel[1])

            if len(panel) > 2 and panel[2]:
                target_width, target_height = panel[2]
                active_panel.setFixedSize(target_width, target_height)

            self.preview_layout.addWidget(active_panel, Qt.AlignmentFlag.AlignCenter)

    def _apply_default_theme(self):
        """Apply the default stylesheet to the preview sandbox on startup."""
        # TODO(AGY): Apply default space theme once preset constants are defined
        pass 
        
    def _toggle_theme(self):
        """Toggle between available stylesheet themes to test dynamic QSS updates."""
        # TODO(AGY): Integrate ThemeService to cycle between Lichess and dark themes
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Use the Fusion style to ensure a clean, consistent native baseline across platforms
    app.setStyle("Fusion")
    
    sandbox = PanelPreviewWindow()
    sandbox.show()
    
    sys.exit(app.exec())