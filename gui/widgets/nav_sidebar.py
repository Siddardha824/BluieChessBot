# gui/widgets/nav_sidebar.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from gui.themes.theme_manager import theme_manager
from gui.core.app_state import app_state

class NavItem(QPushButton):
    """Premium Discord-style circular navigation button with hover styling."""
    def __init__(self, char: str, tooltip: str, page_key: str, parent=None):
        super().__init__(char, parent)
        self.char = char
        self.tooltip = tooltip
        self.page_key = page_key
        self.theme = theme_manager.get_theme()
        
        self.setToolTip(tooltip)
        self.setFixedSize(42, 42)
        self._init_style(active=False)

    def _init_style(self, active: bool) -> None:
        bg_color = self.theme.dark_square.name() if active else "rgba(255, 255, 255, 0.05)"
        text_color = "#FFFFFF" if active else self.theme.panel_text_muted.name()
        border_color = self.theme.console_in.name() if active else "transparent"
        border_radius = "12px" if active else "21px" # Animates from circle to rounded rect

        self.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {bg_color};"
            f"  color: {text_color};"
            f"  border: 1px solid {border_color};"
            f"  border-radius: {border_radius};"
            f"  font-family: 'Outfit';"
            f"  font-size: 13px;"
            f"  font-weight: bold;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background-color: {self.theme.console_in.name()};"
            f"  color: #000000;"
            f"  border-radius: 12px;"
            f"}}"
        )

    def set_active(self, active: bool) -> None:
        self._init_style(active)


class NavSidebar(QWidget):
    page_selected = Signal(str)  # Emitted when a navigation tab is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self.buttons = []
        self._init_ui()

    def _init_ui(self) -> None:
        self.setFixedWidth(64)
        
        # Obidian Sidebar panel style
        self.setStyleSheet(
            f"background-color: #100D1B; "
            f"border-right: 1px solid rgba(0, 229, 255, 0.12);"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # 1. Signature Workbench Icon Logo placeholder at the top
        logo_lbl = QLabel("B")
        logo_lbl.setFixedSize(42, 42)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet(
            f"background-color: qlineargradradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, "
            f"stop:0 #7C4DFF, stop:1 #00E5FF); "
            f"color: #FFFFFF; font-family: 'Outfit'; font-size: 20px; font-weight: bold; border-radius: 8px;"
        )
        layout.addWidget(logo_lbl)
        
        # Divider Line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        layout.addWidget(divider)

        # 2. Main Navigation Items
        nav_items = [
            ("D", "Dashboard Overview", "DASHBOARD"),
            ("A", "Chess Analysis Workspace", "ANALYSIS"),
            ("T", "Tactical & Opening Training", "TRAINING"),
            ("t", "Engine Testing Diagnostics", "TESTING"),
            ("B", "Hardware Benchmarks", "BENCHMARK"),
            ("W", "Auxiliary Chess Tools", "TOOLS"),
            ("S", "System Settings", "SETTINGS")
        ]

        for char, tooltip, page_key in nav_items:
            btn = NavItem(char, tooltip, page_key)
            btn.clicked.connect(lambda checked=False, pk=page_key: self._handle_nav_click(pk))
            self.buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Set default active page highlight
        self.set_active_page("DASHBOARD")

    def _handle_nav_click(self, page_key: str) -> None:
        self.set_active_page(page_key)
        self.page_selected.emit(page_key)

    def set_active_page(self, page_key: str) -> None:
        """Updates the highlighted circular active styles of nav buttons."""
        for btn in self.buttons:
            btn.set_active(btn.page_key == page_key)

    def update_theme(self) -> None:
        """Update styles reactively when the theme is changed."""
        self.theme = theme_manager.get_theme()
        for btn in self.buttons:
            btn.theme = self.theme
            btn.set_active(app_state.active_page == btn.page_key)
