# Step 5: Centipawn Advantage Graph Implementation

This step implements the dynamic Centipawn Advantage Graph panel in the sidebar, which visualizes the computer's real-time position evaluation move-by-move in a beautiful neon line chart.

---

## 📂 1. New Component: `gui/panels/centipawn_graph_widget.py`

This widget utilizes custom 2D painting to render a smooth, animated centipawn advantage curve. It maps the centipawn evaluation score range (clamped between `-4.0` and `+4.0`) to coordinates, rendering a gradient fill area under the curve (cyan glow transitioning to transparent purple) and dots on each move vertex.

### Line-by-Line Explanation:
* **Lines 1-6**: Import standard `QWidget` along with painting utilities (`QPainter`, `QColor`, `QPen`, `QBrush`, `QPolygonF`), coordinate mappings (`QSize`, `Qt`, `QPointF`), and the global `theme_manager`.
* **Lines 8-18**: Define the class `CentipawnGraphWidget(QWidget)`. In the constructor, initialize the active theme, a `history` list (pre-populated with `[0.0]` for an even startup position), and set a fixed visual height constraint between `100px` and `140px`.
* **Lines 20-26**: Implement `add_score(self, cp: float)`. It appends the newest centipawn evaluation score to `self.history`, limits the list to the last 30 moves to ensure readability, and schedules a repaint using `self.update()`.
* **Lines 28-32**: Implement `update_score(self, cp: float)`. During the engine's active search, the latest/current evaluation varies dynamically; this updates the active node without adding a new move.
* **Lines 34-36**: Implement `clear(self)`. Resets `self.history` back to `[0.0]` and schedules a redraw.
* **Lines 38-40**: Implement `update_theme(self, theme)`. Updates the active palette references and triggers a redraw.
* **Lines 42-56**: Implement the core `paintEvent(self, event)`. Creates a `QPainter`, enables antialiasing, draws a semi-transparent dark obsidian background (`rgba(22, 17, 38, 70)`), and draws a 1px border matching the theme's panel border.
* **Lines 58-62**: Render the horizontal center baseline representing `0.0` (even game evaluation) using a light dashed line at 50% height.
* **Lines 64-80**: Loop through the move history and compute scaled coordinates `(x, y)`. The horizontal interval `x_step` is the width divided by the history size. The evaluation scores are clamped between `-4.0` and `+4.0`, mapping the Y coordinate so that positive/advantage scores go upwards and negative/disadvantage scores go downwards.
* **Lines 81-93**: Construct a `QPolygonF` path spanning the points under the baseline, filling it with a soft semi-transparent glowing cyan color (`rgba(0, 229, 255, 25)`).
* **Lines 95-100**: Draw the primary neon-cyan curve connecting adjacent move evaluation nodes using `theme.console_in`.
* **Lines 102-107**: Draw solid, glowing purple circles (`theme.console_out`) at each calculated coordinate vertex.

---

## 📂 2. Modified Component: `gui/main_window.py`

Integrated the graph widget into the main dashboard's right sidebar and wired up the signal slot updates so that player/engine moves and undoes are graphed in real-time.

### Line-by-Line Explanation:
* **Line 8**: Imported `CentipawnGraphWidget` from `gui.panels.centipawn_graph_widget`.
* **Line 106**: Instantiated `self.centipawn_graph` using the active chessboard theme.
* **Line 110**: Added the `self.centipawn_graph` widget to the right sidebar layout with a stretch factor of `1` (positioned between `MoveListWidget` and `EngineInfoWidget`).
* **Lines 169-171**: Connected `move_executed` to call `centipawn_graph.add_score` with the current evaluation bar score.
* **Lines 180-184**: Connected `move_undone` to pop the last score from the graph's history and refresh the visual curve.
* **Lines 200-202**: Connected the engine's `info_received` signal to update the active evaluation node in the graph during searches.
* **Line 260**: Added `self.centipawn_graph.update_theme(active_theme)` inside `change_theme` to guarantee seamless rendering transitions when changing themes.
