# gui/views/settings_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QComboBox, QSlider, QCheckBox, QGridLayout, QFormLayout
)
from PySide6.QtCore import Qt
from gui.themes.theme_manager import theme_manager
from gui.core.app_state import app_state

class SettingsView(QWidget):
    def __init__(self, parent=None):
        """
        Initializes the dynamic Settings View.
        Exposes forms to adjust UCI options, active visual themes, and UI sound options.
        Synchronized fully with preferences.json profile configurations.
        """
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        
        # Mappings of keys to visual display labels
        self.theme_map = {
            "BLUIE_QUANTUM": "Bluie Quantum (Signature)",
            "LICHESS_BLUE": "LiChess Blue/Grey",
            "FOREST_GREEN": "Classic Forest Green"
        }
        
        self._init_ui()
        self.load_values()

        # Connect to theme changes reactively
        app_state.signals.theme_changed.connect(lambda: self.update_theme())

    def _init_ui(self) -> None:
        # Layouts
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(25)
        
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()};")

        # ==========================================
        # 1. HEADER TITLE
        # ==========================================
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        title = QLabel("SYSTEM CONFIGURATION")
        title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 20px; font-weight: 800; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        desc = QLabel("Optimize engine performance, customize board aesthetics, and configure keyboard shortcuts.")
        desc.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 12px; font-weight: 500; "
            f"color: {self.theme.panel_text_muted.name()};"
        )
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        layout.addLayout(header_layout)

        # ==========================================
        # 2. MAIN FORMS CONTAINER (GRID SPLIT)
        # ==========================================
        forms_layout = QHBoxLayout()
        forms_layout.setSpacing(25)

        # ------------------------------------------
        # A. LEFT SECTION: C++ ENGINE OPTION REGISTRY
        # ------------------------------------------
        engine_card = QFrame()
        engine_card.setObjectName("EngineCard")
        engine_layout = QVBoxLayout(engine_card)
        engine_layout.setContentsMargins(25, 25, 25, 25)
        engine_layout.setSpacing(20)

        engine_title = QLabel("C++ ENGINE OPTION REGISTRY")
        engine_title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 13px; font-weight: 700; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        engine_layout.addWidget(engine_title)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setVerticalSpacing(18)
        form.setHorizontalSpacing(20)

        # Hash Size MB Selector
        self.hash_combo = QComboBox()
        self.hash_combo.addItems(["16", "32", "64", "128", "256", "512", "1024"])
        self.hash_combo.currentIndexChanged.connect(self._handle_hash_changed)
        hash_lbl = QLabel("Transposition Size")
        hash_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.panel_text.name()}; text-transform: uppercase;")
        form.addRow(hash_lbl, self.hash_combo)

        # Thread Alloc Slider
        self.threads_slider = QSlider(Qt.Orientation.Horizontal)
        self.threads_slider.setRange(1, 16)
        self.threads_slider.valueChanged.connect(self._handle_threads_changed)
        self.threads_val = QLabel("1")
        self.threads_val.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: {self.theme.console_in.name()};")
        
        threads_box = QHBoxLayout()
        threads_box.addWidget(self.threads_slider)
        threads_box.addWidget(self.threads_val)
        threads_lbl = QLabel("Search Threads")
        threads_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.panel_text.name()}; text-transform: uppercase;")
        form.addRow(threads_lbl, threads_box)

        # Move Overhead Guard Slider
        self.overhead_slider = QSlider(Qt.Orientation.Horizontal)
        self.overhead_slider.setRange(1, 100)
        self.overhead_slider.valueChanged.connect(self._handle_overhead_changed)
        self.overhead_val = QLabel("10ms")
        self.overhead_val.setStyleSheet(f"font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: {self.theme.console_in.name()};")
        
        overhead_box = QHBoxLayout()
        overhead_box.addWidget(self.overhead_slider)
        overhead_box.addWidget(self.overhead_val)
        overhead_lbl = QLabel("Overhead Guard")
        overhead_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.panel_text.name()}; text-transform: uppercase;")
        form.addRow(overhead_lbl, overhead_box)

        engine_layout.addLayout(form)
        engine_layout.addStretch()

        # ------------------------------------------
        # B. RIGHT SECTION: THEME SWAPPER & UI OPTS
        # ------------------------------------------
        ui_card = QFrame()
        ui_card.setObjectName("UiCard")
        ui_layout = QVBoxLayout(ui_card)
        ui_layout.setContentsMargins(25, 25, 25, 25)
        ui_layout.setSpacing(20)

        ui_title = QLabel("AESTHETICS & INTERFACE OPTIONS")
        ui_title.setStyleSheet(
            f"font-family: 'Outfit'; font-size: 13px; font-weight: 700; "
            f"color: {self.theme.console_in.name()}; letter-spacing: 1px;"
        )
        ui_layout.addWidget(ui_title)

        ui_form = QFormLayout()
        ui_form.setContentsMargins(0, 0, 0, 0)
        ui_form.setVerticalSpacing(18)
        ui_form.setHorizontalSpacing(20)

        # Dynamic Theme Swapper
        self.theme_combo = QComboBox()
        for key, name in self.theme_map.items():
            self.theme_combo.addItem(name, key)
        self.theme_combo.currentIndexChanged.connect(self._handle_theme_swapped)
        theme_lbl = QLabel("Color Theme")
        theme_lbl.setStyleSheet(f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {self.theme.panel_text.name()}; text-transform: uppercase;")
        ui_form.addRow(theme_lbl, self.theme_combo)

        # Coordinate Label toggle
        self.coord_chk = QCheckBox("Display rank and file coordinate labels")
        self.coord_chk.stateChanged.connect(self._handle_coords_toggled)
        self.coord_chk.setStyleSheet(f"QCheckBox {{ font-family: 'Outfit'; font-size: 11px; color: {self.theme.panel_text.name()}; }}")
        ui_form.addRow(QLabel(""), self.coord_chk)

        # Sound FX toggle
        self.sounds_chk = QCheckBox("Enable soft game sounds on moves and checks")
        self.sounds_chk.stateChanged.connect(self._handle_sounds_toggled)
        self.sounds_chk.setStyleSheet(f"QCheckBox {{ font-family: 'Outfit'; font-size: 11px; color: {self.theme.panel_text.name()}; }}")
        ui_form.addRow(QLabel(""), self.sounds_chk)

        ui_layout.addLayout(ui_form)
        ui_layout.addStretch()

        forms_layout.addWidget(engine_card, 1)
        forms_layout.addWidget(ui_card, 1)
        layout.addLayout(forms_layout)
        layout.addStretch()

        self.update_stylesheets()

    def load_values(self) -> None:
        """Loads and pre-populates all widgets with current settings from AppState/preferences.json."""
        # 1. Engine options
        opts = app_state.engine_options
        self.hash_combo.setCurrentText(str(opts.get("Hash", 64)))
        
        threads = opts.get("Threads", 1)
        self.threads_slider.setValue(threads)
        self.threads_val.setText(str(threads))
        
        overhead = opts.get("Overhead", 10)
        self.overhead_slider.setValue(overhead)
        self.overhead_val.setText(f"{overhead}ms")

        # 2. UI options
        prefs = app_state.ui_preferences
        self.coord_chk.setChecked(prefs.get("show_coordinates", True))
        self.sounds_chk.setChecked(prefs.get("sounds_enabled", True))

        # 3. Theme
        active_theme_key = app_state.active_theme
        idx = self.theme_combo.findData(active_theme_key)
        if idx != -1:
            self.theme_combo.setCurrentIndex(idx)

    def _handle_hash_changed(self, idx: int) -> None:
        size = int(self.hash_combo.currentText())
        app_state.update_engine_options({"Hash": size})

    def _handle_threads_changed(self, val: int) -> None:
        self.threads_val.setText(str(val))
        app_state.update_engine_options({"Threads": val})

    def _handle_overhead_changed(self, val: int) -> None:
        self.overhead_val.setText(f"{val}ms")
        app_state.update_engine_options({"Overhead": val})

    def _handle_coords_toggled(self, state: int) -> None:
        enabled = self.coord_chk.isChecked()
        app_state.update_ui_preferences({"show_coordinates": enabled})

    def _handle_sounds_toggled(self, state: int) -> None:
        enabled = self.sounds_chk.isChecked()
        app_state.update_ui_preferences({"sounds_enabled": enabled})

    def _handle_theme_swapped(self, idx: int) -> None:
        theme_key = self.theme_combo.currentData()
        if theme_key:
            app_state.active_theme = theme_key
            theme_manager.set_theme(theme_key)

    def update_stylesheets(self) -> None:
        bg_hex = self.theme.panel_background.name()
        border_hex = self.theme.panel_border.name()
        text_hex = self.theme.panel_text.name()
        glow_color = self.theme.console_in.name()

        self.setStyleSheet(
            f"QWidget {{ background-color: {bg_hex}; }}"
            f"QFrame#EngineCard, QFrame#UiCard {{"
            f"  background-color: rgba(22, 17, 38, 0.25);"
            f"  border: 1px solid {border_hex};"
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
            f"  min-width: 140px;"
            f"}}"
            f"QComboBox::drop-down {{"
            f"  border: none;"
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
        )

    def update_theme(self) -> None:
        """Reactive theme updating."""
        self.theme = theme_manager.get_theme()
        self.update_stylesheets()
