# BluieChessBot

A modular open-source chess engine and desktop chess application combining a C++20 chess engine with a Python/PySide6 GUI.

> **Status:** Active development. APIs, architecture, and features are subject to change.

## Overview

BluieChessBot is being developed as a complete chess software stack rather than only an engine. The repository separates the chess engine from the desktop application and connects them through the Universal Chess Interface (UCI).

The project currently contains:

- A C++20 chess engine built with CMake
- Bitboard-based board and attack infrastructure
- Legal move generation
- Position evaluation and search
- Multithreaded search infrastructure
- UCI protocol support
- A Python/PySide6 desktop GUI
- Python chess-state and game-model integration through `python-chess`
- Reusable GUI widgets, panels, services, and models
- Theme and styling infrastructure
- UI component preview tooling
- Automated Python tests and project testing guidelines

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    BluieChessBot                        │
├─────────────────────────────────────────────────────────┤
│  Python Desktop Application                             │
│  PySide6 • UI • Models • Services • Application State   │
├─────────────────────────────────────────────────────────┤
│  Engine Integration                                     │
│  Engine Manager • Sessions • Connector • UCI            │
├─────────────────────────────────────────────────────────┤
│  C++ Chess Engine                                       │
│  Board • Move Generation • Attacks • Evaluation         │
│  Search • Debugging • UCI                               │
└─────────────────────────────────────────────────────────┘
```

The engine is intentionally independent of the GUI. The GUI communicates with an engine process through UCI rather than directly depending on the engine's C++ implementation.

## Requirements

### Engine

- C++20-compatible compiler
- CMake 3.16 or newer
- A platform-supported threading library

### GUI

- Python 3
- PySide6 >= 6.5.0
- python-chess >= 1.10.0

## Build the Engine

Clone the repository:

```bash
git clone https://github.com/Siddardha824/BluieChessBot.git
cd BluieChessBot
```

Configure the engine:

```bash
cmake -S engine -B engine/build
```

Build it:

```bash
cmake --build engine/build
```

For a release build:

```bash
cmake -S engine -B engine/build -DCMAKE_BUILD_TYPE=Release
cmake --build engine/build --config Release
```

## Set Up the GUI

Create a virtual environment from the repository root:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Run the UI Preview

The repository includes a standalone sandbox for previewing selected GUI components without running the complete application:

```bash
python run_ui_preview.py
```

This is useful for iterating on panels, layouts, themes, and component-level styling in isolation.

## Testing

Run the Python test suite with:

```bash
pytest
```

No Tests available for engine currently.

See [`TESTING_GUIDELINES.md`](TESTING_GUIDELINES.md) for project-specific testing practices, [`LOGGING_GUIDELINES.md`](LOGGING_GUIDELINES.md) for logging architecture, and [`COMMENTING_GUIDELINES.md`](COMMENTING_GUIDELINES.md) for documentation conventions.

## UCI Integration

The engine exposes a UCI interface so that the GUI and other compatible chess software can communicate with it as an independent engine process.

The intended communication flow is:

```text
GUI
 │
 │ UCI commands
 ▼
Engine Process
 │
 │ UCI responses
 ▼
GUI
```

This boundary keeps the GUI independent from the engine implementation and makes the engine usable outside the desktop application.

## Contributing

Contributions are welcome.

Before making a substantial change:

1. Read the relevant project documentation.
2. Understand the ownership and boundaries of the component you are changing.
3. Keep changes focused and modular.
4. Add or update tests when behavior changes.
5. Follow the repository's commenting and testing guidelines.
6. Avoid introducing unnecessary dependencies between the GUI and engine layers.

For larger architectural changes, opening an issue before implementation is encouraged so the design can be discussed first.

## License

BluieChessBot is released under the [MIT License](LICENSE).

Copyright (c) 2026 Siddardha Reddy Baddigam

See [`LICENSE`](LICENSE) for the complete license text.

## Third-Party Software

BluieChessBot uses the following open-source projects:

- [Python](https://www.python.org/)
- [PySide6 / Qt for Python](https://doc.qt.io/qtforpython/)
- [python-chess](https://python-chess.readthedocs.io/)
- [CMake](https://cmake.org/)

Their respective licenses and notices remain applicable to those components.

## Author

**Siddardha Reddy Baddigam**

- GitHub: [@Siddardha824](https://github.com/Siddardha824)
- Repository: https://github.com/Siddardha824/BluieChessBot

## Project Status

BluieChessBot is an actively developed project. The repository's architecture and internal APIs are still evolving, so it should currently be considered a development release rather than a stable production application.
