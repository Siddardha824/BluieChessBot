from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QSpinBox, QFileDialog, QHBoxLayout
)
from gui.app.game.models.game_state import GameModes
from gui.utils import get_logger

logger = get_logger(__name__)

class EngineConfigTable(QWidget):
    def __init__(self, app_manager, parent=None):
        super().__init__(parent)
        self._manager = app_manager
        self._game_manager = self._manager.game
        
        self.session_id_1 = "main"
        self.session_id_2 = None
        self._signals_blocked = False
        self._engine_signals_connected = False
        
        self.setup_ui()
        self._connect_ui_signals()

    def setup_ui(self):
        self.setObjectName("engineConfigTable")
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)
        
        # Row 0: Column Headers
        self.lbl_property_header = QLabel("Property", self)
        self.lbl_property_header.setObjectName("propertyHeader")
        self.lbl_property_header.setStyleSheet("font-weight: bold;")
        
        self.lbl_col1 = QLabel("Main Engine", self)
        self.lbl_col1.setObjectName("engine1Header")
        self.lbl_col1.setStyleSheet("font-weight: bold;")
        self.lbl_col1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_col2 = QLabel("Engine 2 (Black)", self)
        self.lbl_col2.setObjectName("engine2Header")
        self.lbl_col2.setStyleSheet("font-weight: bold;")
        self.lbl_col2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.grid.addWidget(self.lbl_property_header, 0, 0)
        self.grid.addWidget(self.lbl_col1, 0, 1)
        self.grid.addWidget(self.lbl_col2, 0, 2)
        
        # Row 1: Executable Path
        self.lbl_path = QLabel("Path:", self)
        
        # Engine 1 Path Layout
        self.widget_path_1 = QWidget(self)
        layout_path_1 = QHBoxLayout(self.widget_path_1)
        layout_path_1.setContentsMargins(0, 0, 0, 0)
        layout_path_1.setSpacing(4)
        self.txt_path_1 = QLineEdit(self)
        self.txt_path_1.setReadOnly(True)
        self.txt_path_1.setObjectName("pathLineEdit1")
        self.btn_browse_1 = QPushButton("...", self)
        self.btn_browse_1.setFixedWidth(30)
        self.btn_browse_1.setObjectName("browseButton1")
        layout_path_1.addWidget(self.txt_path_1, 1)
        layout_path_1.addWidget(self.btn_browse_1)
        
        # Engine 2 Path Layout
        self.widget_path_2 = QWidget(self)
        layout_path_2 = QHBoxLayout(self.widget_path_2)
        layout_path_2.setContentsMargins(0, 0, 0, 0)
        layout_path_2.setSpacing(4)
        self.txt_path_2 = QLineEdit(self)
        self.txt_path_2.setReadOnly(True)
        self.txt_path_2.setObjectName("pathLineEdit2")
        self.btn_browse_2 = QPushButton("...", self)
        self.btn_browse_2.setFixedWidth(30)
        self.btn_browse_2.setObjectName("browseButton2")
        layout_path_2.addWidget(self.txt_path_2, 1)
        layout_path_2.addWidget(self.btn_browse_2)
        
        self.grid.addWidget(self.lbl_path, 1, 0)
        self.grid.addWidget(self.widget_path_1, 1, 1)
        self.grid.addWidget(self.widget_path_2, 1, 2)
        
        # Row 2: Status
        self.lbl_status = QLabel("Status:", self)
        self.lbl_status_1 = QLabel("Disconnected", self)
        self.lbl_status_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status_1.setObjectName("statusLabel1")
        self.lbl_status_2 = QLabel("Disconnected", self)
        self.lbl_status_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status_2.setObjectName("statusLabel2")
        
        self.grid.addWidget(self.lbl_status, 2, 0)
        self.grid.addWidget(self.lbl_status_1, 2, 1)
        self.grid.addWidget(self.lbl_status_2, 2, 2)
        
        # Row 3: Constraint
        self.lbl_constraint = QLabel("Constraint:", self)
        self.combo_constraint_1 = QComboBox(self)
        self.combo_constraint_1.addItems(["Infinite", "Depth", "Time", "Nodes"])
        self.combo_constraint_1.setObjectName("constraintCombo1")
        self.combo_constraint_2 = QComboBox(self)
        self.combo_constraint_2.addItems(["Infinite", "Depth", "Time", "Nodes"])
        self.combo_constraint_2.setObjectName("constraintCombo2")
        
        self.grid.addWidget(self.lbl_constraint, 3, 0)
        self.grid.addWidget(self.combo_constraint_1, 3, 1)
        self.grid.addWidget(self.combo_constraint_2, 3, 2)
        
        # Row 4: Depth Limit
        self.lbl_depth = QLabel("Depth Limit:", self)
        self.spin_depth_1 = QSpinBox(self)
        self.spin_depth_1.setRange(1, 100)
        self.spin_depth_1.setValue(3)
        self.spin_depth_1.setObjectName("depthSpin1")
        self.spin_depth_2 = QSpinBox(self)
        self.spin_depth_2.setRange(1, 100)
        self.spin_depth_2.setValue(4)
        self.spin_depth_2.setObjectName("depthSpin2")
        
        self.grid.addWidget(self.lbl_depth, 4, 0)
        self.grid.addWidget(self.spin_depth_1, 4, 1)
        self.grid.addWidget(self.spin_depth_2, 4, 2)
        
        # Row 5: Time Limit
        self.lbl_time = QLabel("Time Limit:", self)
        self.spin_time_1 = QSpinBox(self)
        self.spin_time_1.setRange(500, 60000)
        self.spin_time_1.setSingleStep(1000)
        self.spin_time_1.setValue(1000)
        self.spin_time_1.setSuffix(" ms")
        self.spin_time_1.setObjectName("timeSpin1")
        self.spin_time_2 = QSpinBox(self)
        self.spin_time_2.setRange(500, 60000)
        self.spin_time_2.setSingleStep(1000)
        self.spin_time_2.setValue(1000)
        self.spin_time_2.setSuffix(" ms")
        self.spin_time_2.setObjectName("timeSpin2")
        
        self.grid.addWidget(self.lbl_time, 5, 0)
        self.grid.addWidget(self.spin_time_1, 5, 1)
        self.grid.addWidget(self.spin_time_2, 5, 2)
        
        # Row 6: Node Limit
        self.lbl_nodes = QLabel("Node Limit:", self)
        self.spin_nodes_1 = QSpinBox(self)
        self.spin_nodes_1.setRange(1000, 100000000)
        self.spin_nodes_1.setSingleStep(100000)
        self.spin_nodes_1.setValue(10000)
        self.spin_nodes_1.setObjectName("nodesSpin1")
        self.spin_nodes_2 = QSpinBox(self)
        self.spin_nodes_2.setRange(1000, 100000000)
        self.spin_nodes_2.setSingleStep(100000)
        self.spin_nodes_2.setValue(10000)
        self.spin_nodes_2.setObjectName("nodesSpin2")
        
        self.grid.addWidget(self.lbl_nodes, 6, 0)
        self.grid.addWidget(self.spin_nodes_1, 6, 1)
        self.grid.addWidget(self.spin_nodes_2, 6, 2)

    def _connect_ui_signals(self):
        # Browse buttons
        self.btn_browse_1.clicked.connect(lambda: self._browse_path(False))
        self.btn_browse_2.clicked.connect(lambda: self._browse_path(True))
        
        # Value change connections
        self.combo_constraint_1.currentTextChanged.connect(self._on_control_changed)
        self.spin_depth_1.valueChanged.connect(self._on_control_changed)
        self.spin_time_1.valueChanged.connect(self._on_control_changed)
        self.spin_nodes_1.valueChanged.connect(self._on_control_changed)
        
        self.combo_constraint_2.currentTextChanged.connect(self._on_control_changed)
        self.spin_depth_2.valueChanged.connect(self._on_control_changed)
        self.spin_time_2.valueChanged.connect(self._on_control_changed)
        self.spin_nodes_2.valueChanged.connect(self._on_control_changed)

    def update_bindings(self, mode: GameModes):
        # Unsubscribe status signals
        self._disconnect_engine_signals()
        
        if mode == GameModes.ENGINE_VS_ENGINE:
            self.session_id_1 = "white_engine"
            self.session_id_2 = "black_engine"
            self.lbl_col1.setText("Engine 1 (White)")
            self.lbl_col2.setText("Engine 2 (Black)")
            self.show_col2(True)
        else:
            self.session_id_1 = "main"
            self.session_id_2 = None
            self.lbl_col1.setText("Main Engine")
            self.show_col2(False)
            
        # Ensure sessions exist
        for sid in [self.session_id_1, self.session_id_2]:
            if sid is not None and not self._manager.engine.has_session(sid):
                self._manager.engine.create_session(sid)
                
        # Subscribe status signals
        self._connect_engine_signals()
        
        # Update settings to match
        self.pull_settings_to_ui()

    def show_col2(self, show: bool):
        self.lbl_col2.setVisible(show)
        self.widget_path_2.setVisible(show)
        self.lbl_status_2.setVisible(show)
        self.combo_constraint_2.setVisible(show)
        self.spin_depth_2.setVisible(show)
        self.spin_time_2.setVisible(show)
        self.spin_nodes_2.setVisible(show)

    def pull_settings_to_ui(self):
        self._block_ui_signals(True)
        
        # Engine 1
        settings_1 = self._game_manager.engine_settings.get(self.session_id_1)
        if settings_1:
            path = settings_1.engine_path
            self.txt_path_1.setText(Path(path).name if path else "Default Build")
            self.txt_path_1.setToolTip(path if path else "Default Build")
            
            session = self._manager.engine.get_session(self.session_id_1)
            status = session.engine_info.status if session else "Disconnected"
            self.lbl_status_1.setText(status)
            self._update_status_style(self.lbl_status_1, status)
            
            self.combo_constraint_1.setCurrentText(settings_1.constraint_mode)
            self.spin_depth_1.setValue(settings_1.max_depth)
            self.spin_time_1.setValue(settings_1.max_time_ms)
            self.spin_nodes_1.setValue(settings_1.max_nodes)
            
        # Engine 2
        if self.session_id_2:
            settings_2 = self._game_manager.engine_settings.get(self.session_id_2)
            if settings_2:
                path = settings_2.engine_path
                self.txt_path_2.setText(Path(path).name if path else "Default Build")
                self.txt_path_2.setToolTip(path if path else "Default Build")
                
                session = self._manager.engine.get_session(self.session_id_2)
                status = session.engine_info.status if session else "Disconnected"
                self.lbl_status_2.setText(status)
                self._update_status_style(self.lbl_status_2, status)
                
                self.combo_constraint_2.setCurrentText(settings_2.constraint_mode)
                self.spin_depth_2.setValue(settings_2.max_depth)
                self.spin_time_2.setValue(settings_2.max_time_ms)
                self.spin_nodes_2.setValue(settings_2.max_nodes)
                
        self._block_ui_signals(False)
        self._update_controls_enabled_states()

    def push_ui_to_settings(self):
        # Engine 1
        settings_1 = self._game_manager.engine_settings.get(self.session_id_1)
        if settings_1:
            settings_1.constraint_mode = self.combo_constraint_1.currentText()
            settings_1.max_depth = self.spin_depth_1.value()
            settings_1.max_time_ms = self.spin_time_1.value()
            settings_1.max_nodes = self.spin_nodes_1.value()
            
        # Engine 2
        if self.session_id_2:
            settings_2 = self._game_manager.engine_settings.get(self.session_id_2)
            if settings_2:
                settings_2.constraint_mode = self.combo_constraint_2.currentText()
                settings_2.max_depth = self.spin_depth_2.value()
                settings_2.max_time_ms = self.spin_time_2.value()
                settings_2.max_nodes = self.spin_nodes_2.value()

    def _update_controls_enabled_states(self):
        # Engine 1
        constraint_1 = self.combo_constraint_1.currentText()
        self.spin_depth_1.setEnabled(constraint_1 == "Depth")
        self.spin_time_1.setEnabled(constraint_1 == "Time")
        self.spin_nodes_1.setEnabled(constraint_1 == "Nodes")
        
        # Engine 2
        if self.session_id_2:
            constraint_2 = self.combo_constraint_2.currentText()
            self.spin_depth_2.setEnabled(constraint_2 == "Depth")
            self.spin_time_2.setEnabled(constraint_2 == "Time")
            self.spin_nodes_2.setEnabled(constraint_2 == "Nodes")

    def _browse_path(self, is_engine_2=False):
        session_id = self.session_id_2 if is_engine_2 else self.session_id_1
        if not session_id:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Engine Executable",
            "",
            "All Files (*)"
        )
        if file_path:
            # Update settings
            self._game_manager.engine_settings[session_id].engine_path = file_path
            
            # Update textbox
            txt_widget = self.txt_path_2 if is_engine_2 else self.txt_path_1
            txt_widget.setText(Path(file_path).name)
            txt_widget.setToolTip(file_path)
            
            # Restart dynamically if running
            session = self._manager.engine.get_session(session_id)
            if session and session.is_running():
                logger.info("Restarting engine session '%s' with new path: %s", session_id, file_path)
                session.stop()
                self._manager.start_engine(engine_path=file_path, session_id=session_id)

    def _update_status_style(self, label: QLabel, status: str):
        label.setProperty("status", status.lower())
        label.style().unpolish(label)
        label.style().polish(label)

    def _on_control_changed(self):
        if self._signals_blocked:
            return
        self.push_ui_to_settings()
        self._update_controls_enabled_states()

    def _block_ui_signals(self, block: bool):
        self._signals_blocked = block

    def _connect_engine_signals(self):
        if self._engine_signals_connected:
            return
            
        session_1 = self._manager.engine.get_session(self.session_id_1)
        if session_1:
            session_1.engine_info.status_changed.connect(self._on_status_1_changed)
            
        if self.session_id_2:
            session_2 = self._manager.engine.get_session(self.session_id_2)
            if session_2:
                session_2.engine_info.status_changed.connect(self._on_status_2_changed)
                
        self._engine_signals_connected = True

    def _disconnect_engine_signals(self):
        if not self._engine_signals_connected:
            return
            
        try:
            session_1 = self._manager.engine.get_session(self.session_id_1)
            if session_1:
                session_1.engine_info.status_changed.disconnect(self._on_status_1_changed)
        except Exception as e:
            logger.debug("Failed to disconnect engine 1 signals: %s", e)
            
        try:
            if self.session_id_2:
                session_2 = self._manager.engine.get_session(self.session_id_2)
                if session_2:
                    session_2.engine_info.status_changed.disconnect(self._on_status_2_changed)
        except Exception as e:
            logger.debug("Failed to disconnect engine 2 signals: %s", e)
            
        self._engine_signals_connected = False

    def _on_status_1_changed(self, status: str):
        self.lbl_status_1.setText(status)
        self._update_status_style(self.lbl_status_1, status)

    def _on_status_2_changed(self, status: str):
        self.lbl_status_2.setText(status)
        self._update_status_style(self.lbl_status_2, status)
