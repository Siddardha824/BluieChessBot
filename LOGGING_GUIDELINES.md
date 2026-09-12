# Standardized Logging Architecture and Guidelines

This document establishes the official logging architecture, level standards, subsystem practices, performance constraints, and verification rules for the **BluieChessBot** project. Adhering to these guidelines ensures cross-stack observability, reliable debugging, zero performance degradation in chess search hot paths, and strict compliance with the Universal Chess Interface (UCI) protocol.

---

## 1. Core Logging Philosophy

Logging in BluieChessBot must adhere to four foundational principles:

1. **High Signal-to-Noise Ratio:** Every log entry must be intentional, actionable, and informative. Avoid spamming logs with repetitive state dumps or uninformative breadcrumbs.
2. **Strict Protocol & Channel Separation:** 
   - The C++ Chess Engine's standard output (`stdout`) is strictly reserved for UCI protocol communication (`uciok`, `readyok`, `bestmove`, `info ...`).
   - Diagnostic and error logging must never pollute the raw UCI pipe.
3. **Zero Overhead in Hot Paths:** Chess engine search loops, move generation, perft routines, and Qt paint events must never perform un-guarded logging or eager string formatting.
4. **Structured & Traceable:** Log messages must follow consistent naming conventions, include relevant domain context (engine role, FEN, move SAN, ply depth), and preserve complete exception tracebacks when errors occur.

---

## 2. Architecture Overview

BluieChessBot consists of two communicating systems across a process boundary. Logging is structured accordingly:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          BluieChessBot                                 │
├────────────────────────────────────────────────────────────────────────┤
│  Python Desktop Application (PySide6 / MVVM)                           │
│  • Logger Hierarchy: gui.utils.logger -> logging.getLogger(__name__)   │
│  • Sinks: Console Stream (Stderr/Stdout) & Rotating File Handler       │
│  • Level Control: BLUIE_LOG_LEVEL environment variable (Default: INFO) │
├───────────────────────────────────┬────────────────────────────────────┤
│  UCI Protocol Boundary (QProcess) │  Captures stdout -> UCI Parser     │
│  • EngineConnector / EngineService│  Captures stderr -> Logger Warning │
├───────────────────────────────────┴────────────────────────────────────┤
│  C++ Chess Engine Subprocess (Bluie)                                   │
│  • UCI Messages: std::cout (Guarded by coutMutex)                      │
│  • Diagnostics: info string <msg> OR std::cerr (Guarded)               │
│  • Debug Utilities: Debug::printBitboard / bluie-debug subcommands     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Log Level Hierarchy & Decision Matrix

We follow standard log levels with strict semantic boundaries across both Python and C++ layers.

| Level | Severity | Purpose | Production Enabled | Typical Scenarios & Examples |
| :--- | :--- | :--- | :---: | :--- |
| **`DEBUG`** | 10 | Diagnostic details for developers. | ❌ No | UCI command parsing tokens, raw bitboard masks, Qt signal emission payloads, cache hits, setting synchronizations. |
| **`INFO`** | 20 | Normal operational milestones and lifecycle events. | ✅ Yes | Application startup/shutdown, engine subprocess launch, game start/termination, PGN/FEN load & save, theme switch. |
| **`WARNING`** | 30 | Recoverable anomalies or unexpected edge cases. | ✅ Yes | Engine response timeout (with recovery), unrecognized optional UCI token, fallback asset loaded, process force-kill on exit. |
| **`ERROR`** | 40 | Failed operations that affect functionality. | ✅ Yes | Engine binary not found, invalid FEN string parse failure, move generation validation failure, file I/O write error. |
| **`CRITICAL`** | 50 | Unrecoverable catastrophic failures causing shutdown. | ✅ Yes | Unhandled exception in Qt main event loop, corrupted transposition table memory allocation, fatal subprocess crash. |

### Level Selection Decision Tree

```text
Is the event a fatal failure halting the application/engine?
├── YES ──► CRITICAL
└── NO  ──► Did a specific action/request fail completely?
            ├── YES ──► ERROR
            └── NO  ──► Is this an unexpected condition/anomaly handled gracefully?
                        ├── YES ──► WARNING
                        └── NO  ──► Is it a milestone in normal user/system workflow?
                                    ├── YES ──► INFO
                                    └── NO  ──► DEBUG (Low-level diagnostic data)
```

---

## 4. Python GUI Logging Architecture

### 4.1. The Logger Factory (`gui.utils.logger`)

All Python modules must obtain their logger instance using the centralized `get_logger` helper:

```python
from gui.utils import get_logger

logger = get_logger(__name__)
```

> [!IMPORTANT]
> Always pass `__name__` as the argument to `get_logger()`. This preserves the Python module namespace hierarchy (e.g., `gui.app.engine.services.engine_connector`), allowing targeted log filtering per package.

### 4.2. Central Configuration & Format Specifications

The central logger configuration in `gui/utils/logger.py` configures log formatters, environment variable overrides, and stream handlers:

* **Console Format:** Lightweight, color-ready, timestamped to the second.
  ```text
  [%(asctime)s] [%(levelname)s] %(name)s: %(message)s
  Date format: %H:%M:%S
  ```
  *Example:* `[14:32:05] [INFO] gui.app.engine.manager.engine_manager: Engine created: White`

* **File Format (Extended):** High-precision timestamp, process/thread identifiers, and exact file line numbers.
  ```text
  %(asctime)s [%(levelname)-8s] [%(threadName)s] [%(name)s:%(lineno)d]: %(message)s
  Date format: %Y-%m-%d %H:%M:%S
  ```
  *Example:* `2026-09-02 14:32:05,123 [INFO    ] [MainThread] [gui.app.game.manager.game_manager:142]: Game started in HumanVsBot mode`

### 4.3. Lazy String Formatting vs. F-Strings

> [!CAUTION]
> Never use eager f-strings or `.format()` inside logger calls. Always use lazy argument formatting (`%s`).

```python
# ❌ BAD: String interpolation executes regardless of whether DEBUG is enabled
logger.debug(f"Computed legal moves for board {board.fen()}: {move_list}")

# ✅ GOOD: String formatting is deferred and evaluated only if DEBUG is enabled
logger.debug("Computed legal moves for board %s: %s", board.fen(), move_list)
```

### 4.4. Guarding Expensive Debug Computations

If generating log arguments requires significant compute (e.g., converting deep move trees, formatting entire board arrays, serializing large JSON structures), wrap the call in `logger.isEnabledFor()`:

```python
if logger.isEnabledFor(logging.DEBUG):
    detailed_history_dump = self._build_complex_debug_history()
    logger.debug("Game history dump: %s", detailed_history_dump)
```

---

## 5. C++ Chess Engine Logging & UCI Rules

The chess engine operates under strict communication constraints governed by the UCI specification.

### 5.1. Strict UCI Compliance on `stdout`

* **The Golden Rule:** `std::cout` is an **I/O protocol channel**, not a general-purpose logging stream.
* Outputting non-UCI-compliant text directly to `std::cout` will corrupt GUI parsers (such as Cutechess, Arena, ChessBase, and Bluie's own GUI).
* All diagnostic messages sent over the UCI pipe must be formatted as:
  ```text
  info string <diagnostic_message>
  ```

### 5.2. Thread-Safe Console Output (`coutMutex`)

Because search calculations run on background worker threads while UCI commands are processed concurrently on the main thread, all `std::cout` emissions must be synchronized using `coutMutex`:

```cpp
// In engine/src/uci/UCI.cpp
{
    std::lock_guard<std::mutex> lock(coutMutex);
    std::cout << "info string ACK: Hash set to " << hashSizeMB << " MB" << std::endl;
}
```

### 5.3. Diagnostic Logging via `std::cerr`

Engine-internal warnings, assertion diagnostic dumps, or unrecoverable fatal errors before exit should be written to `std::cerr`:

```cpp
// In engine/src/Bluie.cpp
catch (const std::exception& e)
{
    std::cerr << "Fatal Engine Error: " << e.what() << std::endl;
    return 1;
}
```

### 5.4. Engine Debug Subcommands (`bluie-debug`)

For developer debugging of bitboards, attack tables, and board states, Bluie provides dedicated `bluie-debug` subcommands wrapped in UCI `info string`:

```cpp
// ✅ Compliant engine debug dump
{
    std::lock_guard<std::mutex> lock(coutMutex);
    std::cout << "info string DEBUG BOARD FEN " << fenPlacement << " " << turnStr << std::endl;
    std::cout << "info string DEBUG BITBOARD WHITE_OCCUPANCY 0x" << std::hex << occ << std::endl;
}
```

---

## 6. Subprocess & Process Boundary Logging

The Python GUI manages the C++ engine lifecycle through `EngineConnector` and `EngineService`.

### 6.1. Boundary Responsibilities

| Channel / Event | Handler | Log Level | Formatting Rule |
| :--- | :--- | :---: | :--- |
| **Command Sent** | `EngineConnector.send_command()` | `DEBUG` | `logger.debug("Sent engine command: %s", command)` |
| **Stdout Received** | `EngineConnector._handle_ready_read_stdout()` | `DEBUG` (Selective) | Handled by UCI parser; raw lines logged at `DEBUG` only if tracing protocol. |
| **Stderr Received** | `EngineConnector._handle_ready_read_stderr()` | `WARNING` | `logger.warning("Engine stderr: %s", stderr_text)` |
| **Process Started** | `EngineConnector.start()` | `INFO` | `logger.info("Starting engine subprocess: %s", executable_path)` |
| **Process Finished** | `EngineConnector._handle_process_finished()` | `INFO` | `logger.info("Engine process finished: code=%s status=%s", code, status)` |
| **Process Crash/Err** | `EngineConnector._handle_process_error()` | `ERROR` | `logger.error("Engine process error: %s", message)` |

---

## 7. Performance & Hot-Path Constraints

Chess engines and desktop UI event loops have microsecond-level latency constraints. Logging in hot paths will severely degrade performance.

### 7.1. Forbidden Logging Locations (Zero Logging)

Never place log calls inside:

1. **Move Generation Loops:** Functions generating pseudo-legal or legal moves (`MoveGen::getLegalMoves`, `MoveHelper.get_legal_moves`).
2. **Search Tree Node Evaluations:** `Search::negamax()`, `Search::alphaBeta()`, `Search::quiescence()`, `Evaluation::evaluate()`.
3. **Perft Loops:** Node traversal performance tests.
4. **Qt Paint Cycles:** `paintEvent()`, `PieceRenderer.draw()`, or canvas refresh routines.
5. **High-Frequency Mouse Handlers:** `mouseMoveEvent()` during piece dragging.

### 7.2. Aggregated Logging Pattern

Instead of logging per node or per move, collect metrics into an accumulator and log once upon completion:

```cpp
// ✅ GOOD: Search metrics logged once per depth iteration or at search completion
std::lock_guard<std::mutex> lock(coutMutex);
std::cout << "info depth " << depth 
          << " score cp " << result.score 
          << " nodes " << result.nodes 
          << " nps " << nps 
          << " time " << duration 
          << " pv " << bestMoveStr << std::endl;
```

---

## 8. Exception & Error Logging Standards

Proper exception logging is critical for post-mortem debugging.

### 8.1. `logger.exception()` vs. `logger.error()`

* **`logger.exception()`**: Use **only** inside an active `except` block. It automatically appends the complete stack traceback (`exc_info=True`).
* **`logger.error()`**: Use when logging a known error condition without a Python exception traceback, or when the traceback adds no value.

```python
# ✅ GOOD: Captures full traceback for unexpected failures
try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(pgn_content)
except OSError as e:
    logger.exception("Failed to write PGN file to path '%s'", file_path)

# ✅ GOOD: Clean error logging for validation failures
if not os.path.exists(engine_path):
    logger.error("Engine executable not found at specified path: %s", engine_path)
```

### 8.2. Qt Slot Exception Boundaries

In PySide6, uncaught exceptions inside Qt Slots can silently corrupt state or crash the application. All major controller slots and background worker slots must be guarded:

```python
@Slot()
def on_start_clicked(self) -> None:
    """Handle user start request safely."""
    try:
        self._manager.start_game()
    except Exception:
        logger.exception("Unhandled error while handling start_game slot")
```

---

## 9. Component Implementation Patterns

### 9.1. Service / Manager Pattern (Backend Logic)

```python
"""Game manager coordinating board state, timers, and engine turns."""

from PySide6.QtCore import QObject, Signal, Slot
from gui.utils import get_logger

logger = get_logger(__name__)


class GameManager(QObject):
    """Manage live chess game progression and turns."""

    game_over = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        logger.debug("GameManager instance initialized")

    def make_move(self, uci_move: str) -> bool:
        """Apply a move to the active game state."""
        logger.info("Processing move: %s", uci_move)
        
        try:
            success = self._apply_move_internal(uci_move)
            if not success:
                logger.warning("Move rejected by validator: %s", uci_move)
                return False
            return True
        except Exception:
            logger.exception("Unexpected error while applying move %s", uci_move)
            return False
```

### 9.2. UI Panel Pattern (View Layer)

In the MVVM View layer, log **user intents** and **lifecycle events**, but keep UI widgets dumb and decoupled:

```python
"""Move history panel displaying PGN move list and navigation controls."""

from PySide6.QtWidgets import QWidget
from gui.utils import get_logger

logger = get_logger(__name__)


class MoveHistoryPanel(QWidget):
    """Display move history with navigation buttons."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        logger.debug("MoveHistoryPanel initialized")

    def handle_step_back_clicked(self) -> None:
        """Handle step back button click."""
        logger.info("Navigation intent: Step back requested")
        self.step_back_requested.emit()
```

---

## 10. Environment Configuration & File Management

### 10.1. Environment Variables

| Variable | Values | Default | Description |
| :--- | :--- | :---: | :--- |
| `BLUIE_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` | Global log severity threshold for Python components. |
| `BLUIE_LOG_FILE` | File system path | *None* | Path to write persistent rotating log files. |

### 10.2. Log Rotation Rules

When file logging is enabled:
- **Max File Size:** `5 MB` per log file.
- **Backup Count:** Maximum of `3` rotated backup files (`bluie.log`, `bluie.log.1`, `bluie.log.2`).
- **Encoding:** Always `UTF-8`.
- **Default Directory:** `~/.bluie/logs/` or `logs/` relative to project root.

---

## 11. Testing & Verification of Logs

Log output must be verified in automated test suites to ensure error handling and diagnostics function properly.

### 11.1. Testing with Pytest `caplog`

Use pytest's built-in `caplog` fixture to assert on log output, level, and message content:

```python
import logging
from gui.app.engine.services.engine_connector import EngineConnector


def test_engine_start_nonexistent_file_logs_error(caplog, qtbot):
    """Verify that attempting to start a missing binary logs an ERROR."""
    connector = EngineConnector(parent=None)
    
    with caplog.at_level(logging.ERROR):
        result = connector.start("/non/existent/path/bluie_engine")
        
    assert result is False
    assert "Engine executable not found: /non/existent/path/bluie_engine" in caplog.text
```

### 11.2. Verification Checklist for Code Reviews

When reviewing pull requests, ensure:
- [ ] No `print()` calls exist in Python codebase (use `logger.*`).
- [ ] No raw `std::cout` calls exist in C++ outside the synchronized UCI protocol output.
- [ ] No eager f-strings are used inside `logger.*()` calls (use `%s`).
- [ ] No logging is placed in hot loops (search, movegen, perft, paintEvent).
- [ ] All `except` blocks use `logger.exception()` or explicitly structured `logger.error()`.
- [ ] New modules obtain their logger via `logger = get_logger(__name__)`.
