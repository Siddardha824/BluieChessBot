from PySide6.QtWidgets import QComboBox, QListView


def configure_combobox_popup(combo: QComboBox) -> None:
    """Install a QListView popup so combo-box QSS behaves consistently."""
    view = QListView()
    view.setMouseTracking(True)
    combo.setView(view)
