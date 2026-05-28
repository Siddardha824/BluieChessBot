# gui/views/benchmark_view.py

import psutil
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QGridLayout
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from gui.themes.theme_manager import theme_manager

class NPSRadialGauge(QWidget):
    """
    A premium, custom-painted circular radial arc gauge representing the active
    Engine Nodes Per Second (NPS) calculation speed.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nps = 0.0
        self.max_nps = 10000000.0  # Dynamic scale up to 10M NPS baseline
        self.setMinimumSize(180, 180)
        self.setMaximumSize(240, 240)

    def set_nps(self, val: float) -> None:
        self.nps = val
        if val > self.max_nps:
            self.max_nps = val * 1.2  # Dynamic auto-scaling
        self.update()

    def clear(self) -> None:
        self.nps = 0.0
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        side = min(w, h)
        rect = QRectF((w - side) / 2.0 + 15, (h - side) / 2.0 + 15, side - 30, side - 30)

        # Draw dark track arc representing the full capacity path
        bg_pen = QPen(QColor(22, 17, 38, 120), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        # Circular gauge covers 240 degrees, starting at -210 degrees
        painter.drawArc(rect, -210 * 16, -240 * 16)

        # Draw glowing neon active arc representation
        pct = min(1.0, max(0.0, self.nps / self.max_nps))
        if pct > 0:
            active_pen = QPen(QColor(0, 229, 255), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            painter.drawArc(rect, -210 * 16, int(-240 * 16 * pct))

        # Render numeric details in the center core
        painter.setPen(QColor(224, 247, 250))  # Arctic silver
        painter.setFont(theme_manager.get_font("Outfit", 18, weight=700))
        nps_text = f"{self.nps / 1e6:.2f} M" if self.nps >= 1e6 else f"{int(self.nps):,}"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, nps_text)

        # Draw units label under the central numbers
        painter.setPen(QColor(176, 190, 197))  # Soft body text
        painter.setFont(theme_manager.get_font("Outfit", 9, weight=400))
        label_rect = QRectF(rect.left(), rect.top() + 45, rect.width(), rect.height() - 45)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, "Nodes / Sec")


class ThreadScalingChart(QWidget):
    """
    Custom 2D-painted line chart that visualizes thread performance scaling
    curves in our cybernetic signature theme.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = []  # List of tuples: (threads, nps)
        self.setMinimumHeight(140)

    def set_data(self, points) -> None:
        self.points = sorted(points, key=lambda x: x[0])
        self.update()

    def clear(self) -> None:
        self.points = []
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Canvas bounds padding margins
        left_pad, right_pad = 45, 15
        top_pad, bottom_pad = 15, 25
        graph_w = w - left_pad - right_pad
        graph_h = h - top_pad - bottom_pad

        # Draw background grid panels
        bg_brush = QBrush(QColor(22, 17, 38, 70))
        painter.fillRect(0, 0, w, h, bg_brush)
        border_pen = QPen(QColor(0, 229, 255, 30), 1)
        painter.setPen(border_pen)
        painter.drawRect(0, 0, w - 1, h - 1)

        # Baseline horizontal axis
        painter.drawLine(left_pad, h - bottom_pad, w - right_pad, h - bottom_pad)

        if not self.points:
            # Draw placeholder state
            painter.setPen(QColor(176, 190, 197, 80))
            painter.setFont(theme_manager.get_font("Outfit", 11, weight=400))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "No scaling data yet. Run Benchmark.")
            return

        # Determine limits
        max_threads = max(p[0] for p in self.points)
        min_threads = min(p[0] for p in self.points)
        max_nps = max(p[1] for p in self.points)
        if max_nps <= 0:
            max_nps = 1e6

        # Draw horizontal grid ticks
        grid_pen = QPen(QColor(255, 255, 255, 15), 1, Qt.PenStyle.DashLine)
        label_pen = QPen(QColor(176, 190, 197, 180))
        painter.setFont(theme_manager.get_font("Outfit", 8))
        
        ticks = 3
        for i in range(ticks + 1):
            y = h - bottom_pad - (i * (graph_h / float(ticks)))
            painter.setPen(grid_pen)
            painter.drawLine(left_pad, y, w - right_pad, y)
            
            # Print NPS label in millions
            val = (max_nps / float(ticks)) * i
            painter.setPen(label_pen)
            painter.drawText(5, y - 6, left_pad - 10, 12, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{val / 1e6:.1f}M")

        # Map and paint vertices
        mapped_points = []
        thread_range = max_threads - min_threads if max_threads != min_threads else 1.0
        
        for threads, nps in self.points:
            x = left_pad + ((threads - min_threads) / float(thread_range)) * graph_w if max_threads != min_threads else left_pad + graph_w / 2.0
            y = h - bottom_pad - (nps / float(max_nps)) * graph_h
            mapped_points.append(QPointF(x, y))

        # Fill color polygons under curve
        if len(mapped_points) > 1:
            poly = QPolygonF()
            poly.append(QPointF(mapped_points[0].x(), h - bottom_pad))
            for pt in mapped_points:
                poly.append(pt)
            poly.append(QPointF(mapped_points[-1].x(), h - bottom_pad))
            
            fill_brush = QBrush(QColor(0, 229, 255, 18))
            painter.setBrush(fill_brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(poly)

        # Draw line connecting
        line_pen = QPen(QColor(0, 229, 255), 2)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(len(mapped_points) - 1):
            painter.drawLine(mapped_points[i], mapped_points[i+1])

        # Draw node spots at intersections
        spot_brush = QBrush(QColor(124, 77, 255))
        painter.setBrush(spot_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        for idx, pt in enumerate(mapped_points):
            painter.drawEllipse(pt, 4, 4)
            # Label the thread count
            threads_count = self.points[idx][0]
            painter.setPen(label_pen)
            painter.drawText(pt.x() - 10, h - bottom_pad + 5, 20, 15, Qt.AlignmentFlag.AlignCenter, f"T{threads_count}")


class BenchmarkView(QWidget):
    """
    Interactive Benchmarking Suite page inside the navigation stacked stack.
    Allows executing multithreaded perft search evaluations, measuring true
    aggregate NPS speed, and plotting parallel thread-scaling ratios.
    """
    def __init__(self, engine_manager=None, parent=None):
        super().__init__(parent)
        self.engine_manager = engine_manager
        self.theme = theme_manager.get_theme()
        
        # State tracking
        self.bench_points = []
        self.bench_threads_list = []
        self.current_bench_idx = 0
        self.is_running = False
        
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Left panel: Visual Gauges & NPS Charts
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        gauge_container = QWidget()
        gauge_container.setStyleSheet("background-color: rgba(22, 17, 38, 0.70); border: 1px solid rgba(0, 229, 255, 0.12); border-radius: 12px;")
        gauge_layout = QVBoxLayout(gauge_container)
        gauge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.gauge = NPSRadialGauge()
        gauge_layout.addWidget(self.gauge)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-family: 'Outfit'; font-size: 13px; font-weight: bold; color: #B0BEC5;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gauge_layout.addWidget(self.status_label)

        left_layout.addWidget(gauge_container, stretch=3)

        self.chart = ThreadScalingChart()
        left_layout.addWidget(self.chart, stretch=2)
        
        layout.addWidget(left_panel, stretch=3)

        # Right panel: Controls & Settings Configuration Form
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: rgba(22, 17, 38, 0.70); border: 1px solid rgba(0, 229, 255, 0.12); border-radius: 12px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        title = QLabel("Engine Analytics & Scaling")
        title.setStyleSheet(f"font-family: 'Outfit'; font-size: 16px; font-weight: bold; color: {self.theme.console_in.name()};")
        right_layout.addWidget(title)

        desc = QLabel("Measures raw leaf node calculation speeds across concurrent CPU hardware threads to analyze multithreading efficiency.")
        desc.setStyleSheet("font-family: 'Outfit'; font-size: 11px; color: #B0BEC5; line-height: 14px;")
        desc.setWordWrap(True)
        right_layout.addWidget(desc)

        # Form Layout of parameters
        form_widget = QWidget()
        grid = QGridLayout(form_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(15)

        # Slider 1: Target Depth
        grid.addWidget(QLabel("Target Depth:", form_widget), 0, 0)
        self.depth_label = QLabel("4")
        self.depth_label.setStyleSheet("font-weight: bold; color: #00E5FF;")
        grid.addWidget(self.depth_label, 0, 1, Qt.AlignmentFlag.AlignRight)
        
        self.depth_slider = QSlider(Qt.Orientation.Horizontal)
        self.depth_slider.setRange(2, 5)  # 2 to 5 standard limits for quick runs
        self.depth_slider.setValue(4)
        self.depth_slider.valueChanged.connect(lambda val: self.depth_label.setText(str(val)))
        grid.addWidget(self.depth_slider, 1, 0, 1, 2)

        # Slider 2: Max Threads
        grid.addWidget(QLabel("Maximum Threads:", form_widget), 2, 0)
        core_count = psutil.cpu_count(logical=True) or 4
        self.threads_label = QLabel(str(core_count))
        self.threads_label.setStyleSheet("font-weight: bold; color: #00E5FF;")
        grid.addWidget(self.threads_label, 2, 1, Qt.AlignmentFlag.AlignRight)

        self.threads_slider = QSlider(Qt.Orientation.Horizontal)
        self.threads_slider.setRange(1, min(16, core_count))
        self.threads_slider.setValue(core_count)
        self.threads_slider.valueChanged.connect(lambda val: self.threads_label.setText(str(val)))
        grid.addWidget(self.threads_slider, 3, 0, 1, 2)

        right_layout.addWidget(form_widget)

        # Separator line
        line = QWidget()
        line.setMinimumHeight(1)
        line.setMaximumHeight(1)
        line.setStyleSheet("background-color: rgba(0, 229, 255, 0.12);")
        right_layout.addWidget(line)

        # Metrics values overview labels
        metrics_title = QLabel("Session Results")
        metrics_title.setStyleSheet("font-family: 'Outfit'; font-size: 12px; font-weight: bold; color: #B0BEC5;")
        right_layout.addWidget(metrics_title)

        self.peak_label = QLabel("Peak Performance: N/A")
        self.peak_label.setStyleSheet("font-family: 'Outfit'; font-size: 11px; color: #E0F7FA;")
        right_layout.addWidget(self.peak_label)

        self.scaling_label = QLabel("Thread Efficiency: N/A")
        self.scaling_label.setStyleSheet("font-family: 'Outfit'; font-size: 11px; color: #E0F7FA;")
        right_layout.addWidget(self.scaling_label)

        right_layout.addStretch()

        # Run Button
        self.run_btn = QPushButton("Run Benchmark Suite")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #00E5FF;
                color: #0B0813;
                font-family: 'Outfit';
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00B2CC;
            }
            QPushButton:disabled {
                background-color: rgba(0, 229, 255, 0.10);
                color: rgba(176, 190, 197, 0.40);
                border: 1px solid rgba(0, 229, 255, 0.15);
            }
        """)
        self.run_btn.clicked.connect(self.start_benchmark)
        right_layout.addWidget(self.run_btn)

        layout.addWidget(right_panel, stretch=2)

    def _connect_signals(self) -> None:
        if self.engine_manager:
            self.engine_manager.bench_total.connect(self._handle_bench_result)

    def set_engine_manager(self, mgr) -> None:
        self.engine_manager = mgr
        self._connect_signals()

    def start_benchmark(self) -> None:
        if not self.engine_manager or self.is_running:
            return
        
        self.is_running = True
        self.run_btn.setEnabled(False)
        self.depth_slider.setEnabled(False)
        self.threads_slider.setEnabled(False)
        
        # Clear stats
        self.bench_points = []
        self.gauge.clear()
        self.chart.clear()
        self.peak_label.setText("Peak Performance: Running...")
        self.scaling_label.setText("Thread Efficiency: Running...")

        # Build list of threads to test sequentially: e.g. [1, 2, 4, 8] up to maximum user threads
        max_threads = self.threads_slider.value()
        self.bench_threads_list = []
        
        # Sequentially select threads: 1, 2, 4, 8, ... and add max_threads if not already present
        curr = 1
        while curr <= max_threads:
            self.bench_threads_list.append(curr)
            curr *= 2
        if max_threads not in self.bench_threads_list:
            self.bench_threads_list.append(max_threads)
            
        self.bench_threads_list = sorted(list(set(self.bench_threads_list)))
        self.current_bench_idx = 0
        
        # Run first benchmark step
        self.run_next_bench_step()

    def run_next_bench_step(self) -> None:
        if self.current_bench_idx >= len(self.bench_threads_list):
            self.finish_benchmark()
            return
            
        threads = self.bench_threads_list[self.current_bench_idx]
        depth = self.depth_slider.value()
        self.status_label.setText(f"Status: Testing {threads} Thread{'s' if threads > 1 else ''}...")
        
        # Send command: bench <depth> <threads>
        self.engine_manager.send_command(f"bench {depth} {threads}")

    def _handle_bench_result(self, nps: int, nodes: int, time_ms: int) -> None:
        if not self.is_running:
            return
            
        threads = self.bench_threads_list[self.current_bench_idx]
        self.bench_points.append((threads, float(nps)))
        
        # Update UI visuals
        self.gauge.set_nps(float(nps))
        self.chart.set_data(self.bench_points)
        
        # Advance test state
        self.current_bench_idx += 1
        self.run_next_bench_step()

    def finish_benchmark(self) -> None:
        self.is_running = False
        self.run_btn.setEnabled(True)
        self.depth_slider.setEnabled(True)
        self.threads_slider.setEnabled(True)
        self.status_label.setText("Status: Complete!")

        # Analyze scaling and print peak
        if self.bench_points:
            peak = max(p[1] for p in self.bench_points)
            self.peak_label.setText(f"Peak Performance: {peak / 1e6:.2f} MNPS" if peak >= 1e6 else f"Peak Performance: {int(peak):,} NPS")
            
            # Efficiency calculation: NPS(max) / (NPS(1) * max_threads)
            nps_1 = next((p[1] for p in self.bench_points if p[0] == 1), 0.0)
            if nps_1 > 0:
                max_pt = max(self.bench_points, key=lambda x: x[0])
                efficiency = (max_pt[1] / (nps_1 * max_pt[0])) * 100.0
                self.scaling_label.setText(f"Thread Efficiency: {efficiency:.1f}% ({max_pt[0]}T vs 1T)")
            else:
                self.scaling_label.setText("Thread Efficiency: N/A")

    def update_theme(self) -> None:
        self.theme = theme_manager.get_theme()
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()};")
        self.update()
