# gui/views/analysis/styles/analysis_styles.py

def get_main_view_style(theme) -> str:
    return f"background-color: {theme.panel_background.name()};"

def get_title_lbl_style(theme) -> str:
    return (
        f"font-family: 'Outfit'; font-size: 18px; font-weight: 800; "
        f"color: {theme.console_in.name()}; letter-spacing: 0.5px;"
    )

def get_header_line_style(theme) -> str:
    return f"color: {theme.panel_border.name()}; border: 1px solid {theme.panel_border.name()};"

def get_panel_title_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 13px; font-weight: 700; color: {theme.panel_text_muted.name()};"

def get_toolbar_button_style(theme) -> str:
    return (
        f"QPushButton {{"
        f"  background-color: rgba(255, 255, 255, 0.05);"
        f"  color: {theme.panel_text.name()};"
        f"  border: 1px solid {theme.panel_border.name()};"
        f"  border-radius: 4px;"
        f"  padding: 5px 12px;"
        f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
        f"}}"
        f"QPushButton:hover {{"
        f"  background-color: rgba(255, 255, 255, 0.12);"
        f"}}"
    )

def get_big_score_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 32px; font-weight: 800; color: {theme.console_info.name()};"

def get_score_desc_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 11px; font-weight: 600; color: {theme.panel_text_muted.name()};"

def get_depth_title_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 11px; font-weight: 700; color: {theme.panel_text.name()}; text-transform: uppercase;"

def get_depth_progress_style(theme) -> str:
    return (
        f"QProgressBar {{"
        f"  background-color: rgba(255, 255, 255, 0.08);"
        f"  border-radius: 3px;"
        f"}}"
        f"QProgressBar::chunk {{"
        f"  background-color: {theme.console_in.name()};"
        f"  border-radius: 3px;"
        f"}}"
    )

def get_grid_lbl_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 10px; font-weight: bold; color: {theme.panel_text_muted.name()}; text-transform: uppercase;"

def get_grid_val_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: {theme.panel_text.name()};"

def get_section_header_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {theme.console_in.name()}; text-transform: uppercase;"

def get_pv_line_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 11px; font-weight: 500; color: {theme.panel_text.name()}; line-height: 14px;"

def get_table_header_style(theme) -> str:
    return (
        f"QHeaderView::section {{"
        f"  background-color: transparent;"
        f"  color: {theme.panel_text_muted.name()};"
        f"  font-family: 'Outfit'; font-size: 9px; font-weight: bold; text-transform: uppercase;"
        f"  border: none;"
        f"  padding: 4px;"
        f"}}"
    )

def get_table_style(theme) -> str:
    return (
        f"QTableWidget {{"
        f"  background-color: transparent;"
        f"  border: none;"
        f"  color: {theme.panel_text.name()};"
        f"  font-family: 'Outfit'; font-size: 11px;"
        f"}}"
        f"QTableWidget::item {{"
        f"  padding: 4px;"
        f"}}"
    )

def get_tab_moves_active_style(theme) -> str:
    return f"QPushButton {{ background: transparent; color: {theme.console_in.name()}; font-family: 'Outfit'; font-size: 11px; font-weight: bold; border: none; border-bottom: 2px solid {theme.console_in.name()}; padding-bottom: 2px; }}"

def get_tab_inactive_style(theme) -> str:
    return f"QPushButton {{ background: transparent; color: {theme.panel_text_muted.name()}; font-family: 'Outfit'; font-size: 11px; font-weight: bold; border: none; }}"

def get_icon_button_style(theme) -> str:
    return (
        f"QPushButton {{"
        f"  background-color: rgba(255, 255, 255, 0.05);"
        f"  border: 1px solid {theme.panel_border.name()};"
        f"  border-radius: 4px;"
        f"  padding: 5px;"
        f"  min-width: 32px; min-height: 32px;"
        f"  font-size: 14px;"
        f"}}"
        f"QPushButton:hover {{"
        f"  background-color: rgba(255, 255, 255, 0.12);"
        f"}}"
    )

def get_new_search_button_style() -> str:
    return (
        f"QPushButton {{"
        f"  background-color: #1F456E;"
        f"  color: white;"
        f"  border: none; border-radius: 4px; padding: 10px;"
        f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
        f"}}"
        f"QPushButton:hover {{"
        f"  background-color: #2b5c91;"
        f"}}"
    )

def get_stop_button_style() -> str:
    return (
        f"QPushButton {{"
        f"  background-color: #8B0000;"
        f"  color: white;"
        f"  border: none; border-radius: 4px; padding: 10px;"
        f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
        f"}}"
        f"QPushButton:hover {{"
        f"  background-color: #a30000;"
        f"}}"
    )

def get_quick_secondary_button_style(theme) -> str:
    return (
        f"QPushButton {{"
        f"  background-color: #1C1A27;"
        f"  color: {theme.panel_text.name()};"
        f"  border: 1px solid {theme.panel_border.name()}; border-radius: 4px; padding: 10px;"
        f"  font-family: 'Outfit'; font-size: 11px; font-weight: 700;"
        f"}}"
        f"QPushButton:hover {{"
        f"  background-color: rgba(255, 255, 255, 0.06);"
        f"}}"
    )

def get_card_styles(theme) -> str:
    bg_hex = theme.panel_background.name()
    border_hex = theme.panel_border.name()
    return (
        f"QWidget {{ background-color: {bg_hex}; }}"
        f"QFrame#BoardPanel, QFrame#TelemetryPanel, QFrame#MoveLogCard, QFrame#QuickCard {{"
        f"  background-color: rgba(22, 17, 38, 0.25);"
        f"  border: 1px solid {border_hex};"
        f"  border-radius: 6px;"
        f"}}"
    )

def get_dialog_style(theme) -> str:
    return f"background-color: {theme.panel_background.name()}; border: 1px solid {theme.panel_border.name()}; border-radius: 6px;"

def get_dot_indicator_style() -> str:
    return "background-color: #2ECC71; border-radius: 4px;"

def get_move_list_table_style(theme) -> str:
    bg_hex = theme.panel_background.name()
    text_hex = theme.panel_text.name()
    border_hex = theme.panel_border.name()
    return (
        f"QTableWidget {{"
        f"  background-color: {bg_hex};"
        f"  color: {text_hex};"
        f"  border: 1px solid {border_hex};"
        f"  font-family: 'Outfit';"
        f"  font-size: 11px;"
        f"}}"
        f"QTableWidget::item {{"
        f"  padding: 4px;"
        f"  font-weight: 500;"
        f"  border: none;"
        f"}}"
    )

def get_control_label_style(theme) -> str:
    return f"font-family: 'Outfit'; font-size: 10px; font-weight: bold; color: {theme.panel_text_muted.name()}; text-transform: uppercase;"

def get_input_field_style(theme) -> str:
    border_hex = theme.panel_border.name()
    text_hex = theme.panel_text.name()
    return (
        f"QSpinBox, QLineEdit {{"
        f"  background-color: rgba(0, 0, 0, 0.25);"
        f"  border: 1px solid {border_hex};"
        f"  border-radius: 4px;"
        f"  padding: 4px 8px;"
        f"  color: {text_hex};"
        f"  font-family: 'Outfit'; font-size: 11px; font-weight: 600;"
        f"}}"
        f"QSpinBox::up-button, QSpinBox::down-button {{"
        f"  background: transparent;"
        f"  border: none;"
        f"}}"
    )

def get_checkbox_style(theme) -> str:
    return (
        f"QCheckBox {{"
        f"  font-family: 'Outfit'; font-size: 11px; font-weight: bold; color: {theme.panel_text.name()};"
        f"  spacing: 5px;"
        f"}}"
    )


