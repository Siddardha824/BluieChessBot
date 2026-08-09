# Commenting and Docstring Standards (PEP 257 & PySide6)

This document establishes the official standards for code documentation, comments, and docstrings in the **BluieChessBot** project. Adhering to these rules ensures codebase consistency, readability, and compatibility with automated documentation generation tools.

---

## 1. Core Documentation Philosophy

Every piece of documentation must serve a clear purpose. We follow these three principles:

1. **Explain the "Why", not the "What":** Code explains *how* an action is performed; comments must explain *why* it is done that way, especially if the implementation or Qt workaround is non-obvious.
2. **Strict PEP 257 Compliance:** All Python docstrings must strictly adhere to the [PEP 257 Style Guide](https://peps.python.org/pep-0257/).
3. **Keep Docs in Sync:** When modifying logic, you are explicitly responsible for updating the corresponding docstrings and comments. Outdated documentation is worse than no documentation.

---

## 2. Docstring Formatting Rules

### Formatting & Quotes

* **Quotes:** Always use triple double quotes (`"""`) for all docstrings, including one-liners.
* **Grammar:** Docstrings must be written as grammatical sentences (starting with a capital letter and ending with a period).
* **Imperative Mood:** Use the imperative mood for the summary line (e.g., `"Return the active board state."` instead of `"Returns the active board state."`).

### Structure Styles

#### One-Line Docstrings

Used for simple functions, getters, and basic data models. The closing quotes must be on the same line as the opening quotes.

```python
"""Return a normalized copy of the active FEN string."""

```

#### Multi-Line Docstrings

Used for classes, complex methods, and modules.

* A single-line summary (imperative mood, ends with a period).
* Exactly one blank line of spacing.
* A detailed explanation of responsibilities, parameters, and behaviors.
* The closing quotes must be on their own line.

```python
def calculate_score(self) -> int:
    """Calculate the positional evaluation score for the current board.

    The score is calculated based on piece values, pawn structure, and king 
    safety. Positional weights are adjusted depending on the game phase.

    Returns:
        The evaluation score in centipawns (positive for White, negative for Black).
    """

```

---

## 3. Structural Docstring Standards

### 3.1. Module-Level Docstrings

Every Python file must start with a module-level docstring on **Line 1**.

* **Summary Line:** A concise description of the module's primary purpose.
* **Details:** Outline the exported classes, services, and how the module interacts with other subsystems.

```python
"""
Engine settings model for chess engine configuration and search constraints.

This module provides the EngineSettings data model for storing and validating
configurations. Validation occurs at the property setter level to catch
configuration errors early.
"""

```

### 3.2. Class-Level Docstrings

Every class definition must be immediately followed by a docstring.

* **Summary:** What the class represents.
* **Details:** Explain its role in the application architecture (e.g., MVVM Model, Manager Facade, View Widget).
* **Attributes / Signals Section:** Use standard headers to document public attributes or custom Qt signals.

```python
class Engines(QObject):
    """
    Reactive data model managing all connected UCI chess engine subprocesses.

    This class maintains a registry of active chess engines and provides methods to
    add, remove, and query engine instances.

    Signals:
        engine_added (Signal): Emitted when a new engine is successfully added.
        engine_removed (Signal): Emitted when an engine is removed from the registry.
    """

```

### 3.3. Method and Constructor Docstrings

All constructors (`__init__`) and major methods (public and helper) must have a docstring.

* **Constructor:** Document parameters in the `Args:` block. Do not include a `Returns:` block.
* **Methods:** Document the action in the imperative mood, followed by `Args:`, `Returns:`, and `Raises:` sections as needed.

```python
def add_engine(self, name: str) -> EngineStatus | None:
    """Add a new engine to the registry or retrieve an existing one.

    If an engine with the given name already exists, it is returned without
    creating a duplicate.

    Args:
        name: The unique name identifier for the engine.

    Returns:
        The EngineStatus object for the engine, or None if the name is empty.
    """

```

### 3.4. Property Docstrings

* **Getters:** Write a brief one-line imperative docstring describing the property value.
* **Setters:** Document the setter's validation logic, raising of exceptions, or triggered signals.

```python
@property
def max_depth(self) -> int:
    """Return the maximum search depth in plies."""
    return self._max_depth

@max_depth.setter
def max_depth(self, val: int):
    """Set maximum search depth with validation.

    Args:
        val: Positive integer depth in plies.

    Raises:
        ValueError: If val is less than 1.
    """
    if val < 1:
        raise ValueError("Max depth must be a positive integer.")
    self._max_depth = val

```

---

## 4. UI-Specific Guidelines (PySide6 & MVVM)

UI modules require special documentation considerations to clarify layout structure, styling hooks, and user intents.

### 4.1. Widget Class Docstrings

Every UI widget or panel should have a class-level docstring that explains its purpose, its role in the MVVM architecture, and how it fits into the broader UI layout.

* Document the role of the component in the view layer.
* List any specific QSS styling IDs (`objectName`) or custom properties they depend on.

```python
class EngineStatusPanel(StyledWidget):
    """
    Master container for engine status cards.

    This panel displays the connection status and file paths for both the White 
    and Black engines. It routes user intents upwards via signals.

    Styling:
        Relies on the `#engineStatusPanel` ID for QSS styling.
    """

```

### 4.2. Signal Definitions (The "Intents")

In our MVVM implementation, views communicate user interactions upward using Qt Signals.

* Place an inline comment above or next to the signal definition.


* Specify what triggers the signal and what the payload represents.



```python
# Emitted when the user selects a new engine path. Payload: engine_role (str, "White" | "Black")
browse_engine_requested = Signal(str)

```

### 4.3. Method Docstrings (Slots and Initializers)

Major UI methods, especially public slots that the backend updates, require clear documentation.

* Use triple double-quotes immediately under the method definition.



### 4.4. Code Layout & Section Dividers

For larger panels, use section dividers to organize the code visually. This is especially helpful in PySide6 where you have layouts, widgets, signals, and slots all in one file.

```python
# --- UI Initialization ---

# --- Layout Setup ---

# --- Public Slots (State Updates) ---

# --- Private Slots (User Intents) ---

```

---

## 5. Implementation & Inline Comments

### 5.1. Inline Comments

Keep inline comments sparse. Only use them to explain why a complex piece of UI logic was written a certain way, especially if it involves Qt-specific quirks.

* **Format:** Start with `#` followed by exactly one space.
* **Placement:** Always place inline comments on their own line *above* the code block they refer to. Avoid end-of-line comments.
* **Rules:** Do not comment on obvious code operations (e.g., `# Loop through array`). Instead, describe decisions, constraints, or workarounds.

```python
# Create a list copy to avoid modifying the dict during iteration
for name in list(self._active_engines.keys()):
    self.remove_engine(name)

```

### 5.2. TODOs and WIP Comments

If you must leave temporary placeholders or pending tasks:

* Use the uppercase `TODO` keyword.
* Include a short explanation and your name or initials.

```python
# TODO(BSR): Optimize en-passant validation algorithm for speed

```