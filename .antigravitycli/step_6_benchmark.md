# Step 6: Engine Multi-Threaded Benchmark Implementation

This step implements the multi-threaded performance benchmark (`bench`) in the C++ engine, integrates its telemetry stream parsing in the GUI's `EngineManager`, and implements the custom vector-drawn `BenchmarkView` in the PySide6 client.

---

## 📂 1. Modified Component: `engine/include/uci/UCI.hpp`
* **Line 52**: Declared the private member function `void handleBench(const std::vector<std::string>& tokens)` to process incoming `"bench"` UCI requests.

---

## 📂 2. Modified Component: `engine/src/uci/UCI.cpp`
* **Lines 129-132**: Intercepts `"bench"` command inside `UCI::parseCommand` and delegates it to `handleBench`.
* **Lines 772-843**: Implements `UCI::handleBench` which:
  - Parses depth (default 5, clamped 1-6), threads (default numThreads, clamped 1-32), and hash (default hashSizeMB, clamped 16-65536).
  - Emits `info string DEBUG BENCHSTART <depth> <threads> <hash>` to standard output.
  - Spawns `threads` worker threads (`std::thread`) running in parallel.
  - Each thread instantiates a local `Board` copy, parses the starting FEN, and executes `Tools::perft(depth, localBoard)`.
  - Joins workers, measures wall-clock duration in milliseconds, calculates aggregate NPS, and prints `info string DEBUG BENCHTOTAL <nps> <nodes> <time_ms>`.

---

## 📂 3. Modified Component: `gui/engine/engine_manager.py`
* **Lines 46-47**: Declares PySide6 thread-safe signals `bench_start(int, int, int)` and `bench_total(int, int, int)`.
* **Lines 216-225**: Adds matching string routing filters inside `_handle_ready_read_stdout` to intercept custom `BENCHSTART` and `BENCHTOTAL` engine debug lines, parse their space-separated numeric parameters, and emit them via the class signals.

---

## 📂 4. New Component: `gui/views/benchmark_view.py`
* **Lines 7-42**: Implements `NPSRadialGauge(QWidget)` which paints a gorgeous vertical speed radial arc using `QPainter::drawArc`. It colors the background path a dark royal obsidian, and overlays the active speed using a bright neon cyan arc that scales dynamically relative to calculated engine performance benchmarks.
* **Lines 45-121**: Implements `ThreadScalingChart(QWidget)` which paints the thread-scaling coordinates graph. It displays light gray dotted grid lines, labels NPS ranges in millions along the Y-axis, connects threads scaling nodes using a neon-cyan curve, and paints violet intersection vertices (`#7C4DFF`).
* **Lines 124-345**: Implements `BenchmarkView(QWidget)` which creates the layout container:
  - Spacers, headers, descriptions, setting sliders for Target Depth (2-5) and Maximum CPU Threads (1-16 logical cores using `psutil`).
  - Implements the sequential benchmark state runner `start_benchmark`, `run_next_bench_step`, and `_handle_bench_result`.
  - When the user triggers the action, the view sequentially executes `bench` commands for different thread configurations (e.g. 1, 2, 4, 8), aggregates performance results in real-time, plots the final scaling curves, and calculates final multithreading speed efficiencies.

---

## 📂 5. Modified Component: `gui/main_window.py`
* **Line 64**: Updates `self.benchmark_view = BenchmarkView(...)` instantiation to pass the parent `self.game_controller.engine_manager` instance, satisfying direct controller signal bindings.
