# gui/panels/engine_info_widget.py

from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QVBoxLayout, QComboBox
from PySide6.QtCore import Qt, Signal

class EngineInfoWidget(QWidget):
    overlay_mode_changed = Signal(str)

    def __init__(self, theme=None, parent=None):
        """
        Initializes the Engine Info Panel.
        Exposes deep search metrics dynamically formatted and styled using the active theme.
        """
        super().__init__(parent)
        from gui.themes import theme_manager
        self.theme = theme if theme is not None else theme_manager.get_theme()
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Pull panel background dynamically
        bg_hex = self.theme.panel_background.name()
        border_hex = self.theme.panel_border.name()
        self.setStyleSheet(f"background-color: {bg_hex}; border: 1px solid {border_hex};")
        
        self.form = QFormLayout()
        self.form.setVerticalSpacing(8)
        self.form.setHorizontalSpacing(15)
        
        self.depth_val = QLabel("-")
        self.nps_val = QLabel("-")
        self.score_val = QLabel("-")
        self.pv_val = QLabel("-")
        self.best_move_val = QLabel("-")
        
        # Apply premium, theme-synchronized text colors
        lbl_color = self.theme.panel_text_muted.name()
        val_color = self.theme.panel_text.name()
        
        label_style = f"font-weight: bold; color: {lbl_color}; font-family: 'Outfit'; font-size: 11px;"
        value_style = f"font-weight: bold; color: {val_color}; font-family: 'Outfit'; font-size: 13px;"
        
        # Word wrap for PV Line in case it grows very long
        self.pv_val.setWordWrap(True)
        self.pv_val.setMaximumWidth(250)
        
        for name, val_lbl in [
            ("Depth:", self.depth_val), 
            ("Speed (NPS):", self.nps_val),
            ("Evaluation:", self.score_val), 
            ("PV Line:", self.pv_val),
            ("Best Move:", self.best_move_val)
        ]:
            val_lbl.setStyleSheet(value_style)
            
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(label_style)
            
            self.form.addRow(name_lbl, val_lbl)
            
        # Dropdown (ComboBox) for Debug Overlay Modes
        self.overlay_dropdown = QComboBox()
        self.overlay_dropdown.setStyleSheet(
            f"QComboBox {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; "
            f"border: 1px solid {self.theme.panel_border.name()}; border-radius: 3px; padding: 2px 15px 2px 4px; font-family: 'Outfit'; font-size: 11px; }}"
            f"QComboBox QAbstractItemView {{ background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()}; selection-background-color: {self.theme.panel_border.name()}; }}"
        )
        self.overlay_dropdown.addItems([
            "None",
            "White Attacks",
            "Black Attacks",
            "Attacks to Selected (White)",
            "Attacks to Selected (Black)",
            "Engine Legal Moves"
        ])
        self.overlay_dropdown.currentIndexChanged.connect(self._handle_overlay_changed)
        
        overlay_lbl = QLabel("Debug Overlay:")
        overlay_lbl.setStyleSheet(label_style)
        self.form.addRow(overlay_lbl, self.overlay_dropdown)

        layout.addLayout(self.form)
        layout.addStretch()

    def update_engine_data(self, depth: int, nps: int, score: float, pv: str, best_move: str = "-") -> None:
        """
        Dynamically updates the UI label texts based on active search frames.
        """
        self.depth_val.setText(str(depth))
        self.nps_val.setText(f"{nps / 1000:.1f} kN/s" if nps > 0 else "-")
        
        # Colorize score based on advantage (soft green for positive, soft red for negative, normal for even)
        if score > 0.0:
            self.score_val.setText(f"+{score:.2f}")
            self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.console_info.name()}; font-family: 'Outfit'; font-size: 13px;")
        elif score < 0.0:
            self.score_val.setText(f"{score:.2f}")
            self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.console_error.name()}; font-family: 'Outfit'; font-size: 13px;")
        else:
            self.score_val.setText("0.00")
            self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.panel_text.name()}; font-family: 'Outfit'; font-size: 13px;")
            
        self.pv_val.setText(pv)
        self.best_move_val.setText(best_move)

    def update_analysis_state(self, state) -> None:
        """
        Updates the engine metrics using a structured AnalysisState object,
        formatting mate-in-N scores elegantly.
        """
        self.depth_val.setText(str(state.depth))
        self.nps_val.setText(f"{state.nps / 1000:.1f} kN/s" if state.nps > 0 else "-")
        
        # Format Score (Handling Mate vs Centipawn)
        if state.is_mate:
            mate_val = state.mate_in if state.mate_in is not None else 0
            if mate_val > 0:
                self.score_val.setText(f"M{mate_val}")
                self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.console_info.name()}; font-family: 'Outfit'; font-size: 13px;")
            else:
                self.score_val.setText(f"M{mate_val}")
                self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.console_error.name()}; font-family: 'Outfit'; font-size: 13px;")
        else:
            score = state.score
            if score > 0.0:
                self.score_val.setText(f"+{score:.2f}")
                self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.console_info.name()}; font-family: 'Outfit'; font-size: 13px;")
            elif score < 0.0:
                self.score_val.setText(f"{score:.2f}")
                self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.console_error.name()}; font-family: 'Outfit'; font-size: 13px;")
            else:
                self.score_val.setText("0.00")
                self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.panel_text.name()}; font-family: 'Outfit'; font-size: 13px;")
                
        pv_str = " ".join(state.pv) if state.pv else "-"
        self.pv_val.setText(pv_str)
        self.best_move_val.setText(state.best_move if state.best_move else "-")


    def clear(self) -> None:
        """Resets all metrics to default lines."""
        self.depth_val.setText("-")
        self.nps_val.setText("-")
        self.score_val.setText("-")
        self.score_val.setStyleSheet(f"font-weight: bold; color: {self.theme.panel_text.name()}; font-family: 'Outfit'; font-size: 13px;")
        self.pv_val.setText("-")
        self.best_move_val.setText("-")

    def _handle_overlay_changed(self, index: int) -> None:
        mode_map = {
            0: "NONE",
            1: "WHITE_ATTACKS",
            2: "BLACK_ATTACKS",
            3: "ATTACKSTO_WHITE",
            4: "ATTACKSTO_BLACK",
            5: "ENGINE_LEGALS"
        }
        mode = mode_map.get(index, "NONE")
        self.overlay_mode_changed.emit(mode)
