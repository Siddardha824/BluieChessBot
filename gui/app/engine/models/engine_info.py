"""Engine info model for storing chess engine metadata and runtime status.

This module provides the EngineInfo data model for storing UCI chess engine metadata,
capabilities, and runtime status. It serves as a reactive data container that emits
signals when the engine state is updated.

Design: Properties use manual batch updates via notify_updated() to prevent signal
storms when multiple fields are updated in quick succession.
"""

from PySide6.QtCore import QObject, Signal
import inspect


class EngineInfo(QObject):
    """Manage UCI chess engine metadata and runtime status.

    This model stores engine identification (name, author) and current connection/search
    states. It uses Qt signals to notify listeners of state changes, with batch updates
    managed through the notify_updated() method to maintain performance.

    Signals:
        info_updated: Emitted when notify_updated() is called after state modifications.

    Design Pattern:
    - Properties use setters/getters but do NOT emit signals individually.
    - Service code must call notify_updated() explicitly after modifying properties.
    - This prevents signal storms when multiple properties change in rapid succession.
    """

    # Emitted after batch property updates via notify_updated()
    info_updated = Signal()

    def __init__(self, parent, name: str = "", author: str = ""):
        """Initialize the engine info model.

        Args:
            parent: Qt parent object for memory management.
            name: Engine name (e.g., "Stockfish 16").
            author: Engine author name.
        """
        super().__init__(parent)
        self._name = name
        self._author = author
        self._connection_status = "NotRunning"  # NotRunning, Starting, Running, Error
        self._search_status = "Offline"  # Offline, Connecting, Idle, Searching

    # Engine identification properties
    @property
    def name(self) -> str:
        """Return the engine name (e.g., 'Stockfish 16')."""
        return self._name

    @name.setter
    def name(self, val: str):
        """Set the engine name. Do not emit signal; call notify_updated() after."""
        self._name = val

    @property
    def author(self) -> str:
        """Return the engine author name."""
        return self._author

    @author.setter
    def author(self, val: str):
        """Set the engine author. Do not emit signal; call notify_updated() after."""
        self._author = val

    # Engine status properties
    @property
    def connection_status(self) -> str:
        """Return the engine process connection status.

        Possible values: "NotRunning", "Starting", "Running", "Error".
        """
        return self._connection_status

    @connection_status.setter
    def connection_status(self, val: str):
        """Set the connection status. Do not emit signal; call notify_updated() after."""
        self._connection_status = val

    @property
    def search_status(self) -> str:
        """Return the engine search/analysis status.

        Possible values: "Offline", "Connecting", "Idle", "Searching".
        """
        return self._search_status

    @search_status.setter
    def search_status(self, val: str):
        """Set the search status. Do not emit signal; call notify_updated() after."""
        self._search_status = val

    def notify_updated(self) -> None:
        """Emit the info_updated signal to notify listeners of state changes.

        This method should be called by the service after updating one or more
        properties to batch signal emissions and improve performance. Prevent
        signal storms when multiple properties change in rapid succession.

        Usage:
            engine_info.name = "Stockfish"
            engine_info.author = "T. Romstad"
            engine_info.connection_status = "Running"
            engine_info.notify_updated()  # Single signal for all three changes.
        """
        self.info_updated.emit()

    def asdict(self) -> dict:
        """Convert model to dictionary of property names and values.

        Use introspection to dynamically discover all @property members and
        return their current values as a dictionary.

        Returns:
            A dictionary with property names as keys and current values.

        Example:
            >>> engine_info.asdict()
            {'name': 'Stockfish 16', 'author': 'T. Romstad', 
             'connection_status': 'Running', 'search_status': 'Idle'}
        """
        # Use introspection to find all property members on the class
        properties = [
            name for name, val in inspect.getmembers(type(self), lambda v: isinstance(v, property))
        ]

        # Build dictionary by getting current value of each property
        return {
            key: getattr(self, key) for key in properties
        }
