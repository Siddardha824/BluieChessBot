# Testing and Verification Guidelines

This document details the testing philosophy, rules, component-specific constraints, UI testing guidelines, log verification practices with `caplog`, directory structure, and execution practices for unit and integration testing in the **BluieChessBot** project. All tests generated or updated by developers or AI agents must adhere strictly to these standards.

---

## 1. Testing Philosophy & Strategy

**Focus on Logic:** Prioritize testing the core business logic (Models, Managers, and Services) over UI rendering details.

**Decoupled UI Testing:** Test UI components by verifying their signals, slots, and state changes (using `pytest-qt` or `QApplication` event cycles) rather than inspecting pixel rendering or visual styles.

**Regression Safeguards:** When resolving a bug, follow this strict cycle: 
`Bug Identified` ➔ `Write Failing Test Case` ➔ `Implement Fix` ➔ `Verify Test Passes`.

**Arrange-Act-Assert (AAA):** Structure every test clearly with comments or logical spacing dividing setup (**Arrange**), execution (**Act**), and assertions (**Assert**).

**Object Isolation:** Tests must not leak state. Use Pytest fixtures to provide fresh instances of objects for each test method.

**Verify Error Logging with `caplog`:** For failure branches, error handling blocks, and warning paths, use pytest's `caplog` fixture to verify that errors are logged at the correct severity with descriptive messages, without polluting test output. Refer to [`LOGGING_GUIDELINES.md`](LOGGING_GUIDELINES.md) for logging level standards.

**No Unused Imports:** Only import packages, classes, or modules that are explicitly used in the test. Do not import `MagicMock` if only using `@patch`.

**Docstrings:** Every test class and test method must have a descriptive docstring explaining exactly what behavior/scenario it verifies.

---

## 2. Component-Specific Rules

### Pure Logic / Services (e.g., UCI Parser, Helpers)
* Do not use mocks unless absolutely necessary. Test the actual return values of the functions/classes.
* Use `@pytest.mark.parametrize` extensively to batch-test multiple inputs, edge cases, and inverse operations without duplicating test logic.
* Explicitly test error handling and exception blocks (e.g., catching invalid UCI strings).

### State Models (e.g., BoardState)
* Verify data integrity and immutability (e.g., returning copies of arrays/lists instead of references).
* Use the `qtbot` fixture provided by `pytest-qt` to test Qt Signals.
* Wrap actions that emit signals in a `with qtbot.waitSignal(signal, timeout=1000) as blocker:` block.
* Always assert that the payload inside `blocker.args` matches the expected state.
* Navigating `view_index` must change `view_board` FEN without modifying the actual live game board state.

### Controllers & Managers (e.g., BoardManager, GameManager)
* Focus on testing delegation, not business logic (which should be tested in the Services).
* Use `@patch` to mock the underlying Services and Models.
* Verify that the Manager calls the correct underlying methods with the correct arguments using `.assert_called_once_with()`.
* Verify that Qt signals from the underlying Model successfully bubble up through the Manager to the UI layer.
* Verify termination triggers by feeding known game-ending positions (checkmate, stalemate, repetition FENs) and asserting that `GameManager` captures termination, stops searches, and emits `game_over`.

### Error Handling & Log Verification (`caplog`)
* **Test Negative & Edge Paths:** Whenever a service or manager handles an error, catches an exception, or ignores an invalid input, assert that the corresponding log message was generated.
* **Scope Log Level:** Always configure `caplog.at_level()` with the appropriate severity (`logging.WARNING`, `logging.ERROR`, etc.) and optionally specify the logger name to filter out noise from other modules:
  ```python
  with caplog.at_level(logging.ERROR, logger="gui.app.engine.services.engine_connector"):
      connector.start("/invalid/path")
  ```
* **Substring Assertions:** Assert against essential diagnostic keywords in `caplog.text` rather than full timestamped strings:
  ```python
  assert "Engine executable not found" in caplog.text
  ```
* **Strict Tuple Assertions:** For exact level and message validation, check `caplog.record_tuples`:
  ```python
  assert ("gui.app.engine.services.engine_connector", logging.ERROR, "Engine executable not found: /invalid/path") in caplog.record_tuples
  ```
* **Clear State in Multi-Step Tests:** Use `caplog.clear()` between consecutive actions within the same test to prevent earlier log messages from causing false positives.

---

## 3. UI Testing Guidelines (PySide6 & pytest-qt)

Testing UI components requires a fundamental shift in mindset from testing backend services. While backend tests verify logic and state mutations, UI tests must exclusively verify **wiring** and **display**. Because UI widgets are deliberately "dumb", these tests should be fast, isolated, and straightforward.

### The Core Philosophy: Test Wiring, Not Logic
Never test business logic in a UI test. Do not test if the engine actually connects when you click "Browse". Instead, test that clicking "Browse" successfully emits the `browse_requested("White")` signal, and test that calling `update_status("Connected")` changes the text of the status label.

### Isolate the Component Completely
Never import your `AppManager`, `GameMode`, or backend services into a UI test. Instantiate the widget completely naked, passing `parent=None`. If the widget relies on a backend connection, it violates the MVVM separation.

### Test Outbound Intents (User Actions)
Every custom signal your UI defines must have a test proving that a specific UI interaction triggers it with the correct payload. Use `qtbot.mouseClick()` to simulate user interaction, and wrap it in `qtbot.waitSignal()` to verify the emission.

### Test Inbound State (Slots & Updates)
Every public method designed to be called by the `AppManager` or `SignalConnector` must be tested to ensure it mutates the visual tree correctly. Manually call the `update_*` method with dummy data, then assert that the internal `QLabel` or `QWidget` holds that exact data.

### Test Theming Hooks, Not Pixels
Do not test specific hex codes, font sizes, or pixel widths. Stylesheets change, making pixel/color tests brittle. Instead, test that the component has the correct `objectName()` assigned, or that dynamic properties are correctly set so your QSS router can find them.

---

## 4. Template Examples

Place tests in their respective directories following the mirroring rule (e.g., `tests/gui/ui/panels/test_engine_status_panel.py` or `tests/gui/app/engine/services/test_engine_connector.py`).

### 4.1. UI Testing Template (`SingleEngineCard`)

```python
import pytest
from PySide6.QtCore import Qt
from gui.ui.panels.engine_status_panel import SingleEngineCard

class TestSingleEngineCard:
    """Test suite for the isolated SingleEngineCard UI component."""

    def test_initialization_and_theming_hooks(self, qtbot):
        """Verify the widget initializes with default text and correct QSS object names."""
        card = SingleEngineCard(engine_role="White", parent=None)
        qtbot.addWidget(card) 

        assert card.objectName() == "engineCard"
        assert card._role_label.text() == "<b>White Engine</b>"
        assert card._status_label.text() == "Disconnected"
        assert card._path_label.text() == "No engine selected"

    def test_update_slots(self, qtbot):
        """Verify that public update methods correctly mutate the visible labels."""
        card = SingleEngineCard(engine_role="Black", parent=None)
        qtbot.addWidget(card)

        card.update_status("Running")
        card.update_path("C:/engines/stockfish.exe")

        assert card._status_label.text() == "Running"
        assert card._path_label.text() == "C:/engines/stockfish.exe"

    def test_browse_intent_emission(self, qtbot):
        """Verify clicking the browse button emits the intent with the correct role payload."""
        card = SingleEngineCard(engine_role="White", parent=None)
        qtbot.addWidget(card)

        with qtbot.waitSignal(card.browse_requested, timeout=1000) as blocker:
            qtbot.mouseClick(card._browse_button, Qt.MouseButton.LeftButton)

        assert blocker.args == ["White"]
```

### 4.2. Service & Log Verification Template (`EngineConnector` with `caplog`)

```python
import logging
import pytest
from gui.app.engine.services.engine_connector import EngineConnector


class TestEngineConnectorLogging:
    """Test suite verifying logging behavior and error handling in EngineConnector."""

    def test_start_nonexistent_executable_logs_error(self, caplog, qtbot):
        """Verify that attempting to start a missing executable logs an ERROR with path details."""
        # Arrange
        connector = EngineConnector(parent=None)
        invalid_path = "/non/existent/path/bluie_bot"

        # Act
        with caplog.at_level(logging.ERROR, logger="gui.app.engine.services.engine_connector"):
            success = connector.start(invalid_path)

        # Assert
        assert success is False
        assert f"Engine executable not found: {invalid_path}" in caplog.text
        assert any(
            record.levelno == logging.ERROR and "Engine executable not found" in record.message
            for record in caplog.records
        )

    def test_send_command_when_stopped_logs_warning(self, caplog, qtbot):
        """Verify sending a command to a stopped process logs a WARNING."""
        # Arrange
        connector = EngineConnector(parent=None)
        command = "isready"

        # Act
        with caplog.at_level(logging.WARNING, logger="gui.app.engine.services.engine_connector"):
            connector.send_command(command)

        # Assert
        assert "Failed to send command; engine is not running: isready" in caplog.text
```

---

## 5. Test Directory Organization

To ensure maximum discoverability and maintain architectural strictness, the `tests/` directory must act as a perfect mirror of the main project directory. 

### 5.1. The Mirroring Rule
The folder hierarchy inside the `tests/` directory must exactly match the folder hierarchy of the source code. If a module resides deeply nested in the project root, its corresponding test must be located at that exact same nested path within `tests/`.

### 5.2. Naming Convention
A test file must be named by prefixing `test_` to the exact name of the module it is testing: `test_<module_name>.py`. 

### 5.3. Example Structure
Below is an example demonstrating how the source directory translates directly to the test directory:

**Source Code Structure:**
```text
Project_Root/
└── gui/
    ├── app/
    │   ├── game/
    │   │   ├── models/
    │   │   │   └── board_state.py        # Source module
    │   │   └── managers/
    │   │       └── game_manager.py       # Source module
    │   └── engine/
    │       └── services/
    │           └── engine_connector.py   # Source service
    └── ui/
        └── panels/
            └── engine_status_panel.py    # Source UI component
```

**Corresponding Test Structure:**

```text
Project_Root/
└── tests/
    ├── conftest.py                       # Global fixtures at test root
    └── gui/
        ├── app/
        │   ├── game/
        │   │   ├── models/
        │   │   │   └── test_board_state.py        # Mirrored test
        │   │   └── managers/
        │   │       └── test_game_manager.py       # Mirrored test
        │   └── engine/
        │       └── services/
        │           └── test_engine_connector.py   # Mirrored test
        └── ui/
            └── panels/
                └── test_engine_status_panel.py    # Mirrored test
```

---

## 6. Execution Commands

To run tests locally, execute the following commands in the project root. Note that the `pytest-qt` library hooks into standard `pytest` commands automatically.

| Command | Purpose |
| --- | --- |
| `pytest` | Runs all tests, including UI tests (Qt event loop is handled automatically by the plugin). |
| `pytest -v` | Runs all tests with verbose output for better debugging readability. |
| `pytest --cov=gui/app` | Runs tests and generates a code coverage report for the core backend directory. |
| `pytest -k "test_start_nonexistent"` | Runs specific test matching expression. |

---

## 7. Proposal and Verification Formats

### 7.1. Test Plan Proposal Format

When proposing a new test suite, follow this exact structure:

**Test Objective:** [Module / Component]

**Risk Level:** [CRITICAL / HIGH / MEDIUM / LOW]

**Mock Requirements:** [List of dependencies to mock]

**Log Verification:** [Specify expected caplog levels and messages for negative paths]

**Test Case Matrix (Normal):** [Input, expected state, expected signals]

**Test Case Matrix (Edge):** [Illegal moves, corrupted FEN, process crash, log emissions]

**Test Code Blueprint:** [File path, sample code, assertions]

### 7.2. Verification Summary Format

Every review conducted by the Testing Agent must conclude with these precise metrics:

**Coverage Gaps:** Untested branches in the changes.

**Recommended Tests:** List of tests to write (including error log assertions).

**Risk Level:** Project risk assessment of the current build.

**Automation Readiness:** Suitability of the proposed tests for CI/CD gates.

**Overall Confidence:** Score out of 10.