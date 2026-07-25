"""Engine management module for UCI chess engine subprocess coordination.

Provide a reactive data model for managing connections to multiple UCI chess engines
and coordinating their lifecycle events.
"""

from PySide6.QtCore import QObject, Signal
from .engine_status import EngineStatus
from gui.utils import get_logger

logger = get_logger(__name__)


class Engines(QObject):
    """Reactive data model managing all currently connected UCI chess engine subprocesses.

    This class maintains a registry of active chess engines and provides methods to
    add, remove, and query engine instances. It emits Qt signals when engines are
    added or removed, allowing the UI to react to changes in the engine collection.

    Signals:
        engine_added: Emitted when a new engine is successfully added (engine_name, engine_status).
        engine_removed: Emitted when an engine is removed from the registry (engine_name).
    """

    # Signals for reactive updates
    engine_added = Signal(str, object)
    engine_removed = Signal(str)

    def __init__(self, parent):
        """Initialize the Engines data model.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        # Dictionary mapping engine names to their status objects
        self._active_engines: dict[str, EngineStatus] = {}

    @property
    def active_engines(self) -> list[str]:
        """Get a list of all currently active engine names."""
        return list(self._active_engines.keys())

    def get_engine(self, name: str) -> EngineStatus | None:
        """Retrieve a specific engine by name.

        Args:
            name: The name of the engine to retrieve.

        Returns:
            The EngineStatus object if found, None otherwise.
        """
        return self._active_engines.get(name)

    def add_engine(self, name: str) -> EngineStatus | None:
        """Add a new engine to the registry or retrieve an existing one.

        If an engine with the given name already exists, return it without
        creating a duplicate. New engines are initialized with an EngineStatus
        object and registered in the model tree.

        Args:
            name: The unique name identifier for the engine.

        Returns:
            The EngineStatus object for the engine (new or existing), or None if
            the name is empty.
        """
        # Validate that a name was provided
        if not name:
            logger.warning("Cannot add an engine without a name")
            return None

        # Return existing engine if already registered
        if name in self._active_engines:
            logger.warning("An engine with this name exists: %s", name)
            return self._active_engines[name]

        # Create and register new engine
        status = EngineStatus(self)
        self._active_engines[name] = status
        logger.info("Engine registered in model tree: %s", name)

        # Notify listeners of the new engine
        self.engine_added.emit(name, status)
        return status

    def remove_engine(self, name: str) -> None:
        """Remove an engine from the registry and clean up its resources.

        Properly tear down the engine by calling deleteLater() to ensure
        Qt handles cleanup on the next event loop iteration.

        Args:
            name: The name of the engine to remove.
        """
        # Remove from registry and get the engine object
        engine = self._active_engines.pop(name, None)

        if engine is not None:
            logger.info("Engine removed from model tree: %s", name)
            # Schedule the engine object for deletion
            engine.deleteLater()
            # Notify listeners of the removal
            self.engine_removed.emit(name)

    def clear(self) -> None:
        """Remove all engines from the registry.

        Iterate through all registered engines and remove them one by one,
        ensuring proper cleanup of each engine's resources.
        """
        # Create a list copy to avoid modifying dict during iteration
        for name in list(self._active_engines.keys()):
            self.remove_engine(name)