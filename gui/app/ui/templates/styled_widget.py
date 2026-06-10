from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

class StyledWidget(QWidget):
    def __init__(self, object_name="",parent=None):
        super().__init__(parent)

        self.setObjectName(object_name)

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True
        )