"""
Core base widget implementation supporting unified QSS styling and interaction hooks.

This module provides the StyledWidget class, which serves as the base class for
custom UI widgets in the application, ensuring QSS properties are correctly polished.
"""

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QMouseEvent


class StyledWidget(QWidget):
    """
    Base QWidget subclass configured for dynamic styling and event propagation.

    This class enables stylesheet styling via Qt style sheets (QSS) by setting the
    WA_StyledBackground attribute. It also provides a unified 'clicked' signal
    and a helper to update QSS properties dynamically.

    Signals:
        clicked (Signal): Emitted when the widget is clicked with the left mouse button.
    """

    # --- Signals ---

    # Emitted on left mouse button click
    clicked = Signal()

    # --- UI Initialization ---

    def __init__(self, object_name: str, parent: QWidget):
        """Initialize the styled widget base class.

        Args:
            object_name: The QObject name used as a selector in stylesheet definitions.
            parent: The parent QWidget.
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)

        # Force WA_StyledBackground to allow style sheet styling on custom QWidget subclasses
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the layout and child widgets.

        Subclasses should override this method to perform layout and widget initialization.
        """
        pass

    # --- Public Slots (State Updates) ---

    def update_state(self, property_name: str, value: Any):
        """Update a dynamic styling property and polish the widget to apply changes.

        Args:
            property_name: The name of the stylesheet property.
            value: The value to apply to the property.
        """
        self.setProperty(property_name, value)
        self.style().polish(self)

    # --- Event Handlers ---

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events to emit the clicked signal on left-click.

        Args:
            event: The QMouseEvent object containing event details.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)

