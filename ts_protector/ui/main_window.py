"""
Main Window UI for TS Protector Pro
PyQt6 implementation with modern dark theme
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QComboBox,
    QTextEdit, QGroupBox, QFrame, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QAction
from pathlib import Path


class MainWindow(QMainWindow):
    """Main application window"""

    # Signals
    connect_clicked = pyqtSignal()
    disconnect_clicked = pyqtSignal()
    auto_detect_changed = pyqtSignal(bool)
    start_with_windows_changed = pyqtSignal(bool)
    minimize_to_tray_changed = pyqtSignal(bool)
    server_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_connected = False
        self.init_ui()
        self.load_stylesheet()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TS Protector Pro")
        self.setFixedSize(400, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

        # Title
        title_layout = self.create_title_section()
        main_layout.addLayout(title_layout)

        # Separator
        main_layout.addWidget(self.create_separator())

        # Status section
        status_layout = self.create_status_section()
        main_layout.addLayout(status_layout)

        # Connect button
        self.connect_btn = self.create_connect_button()
        main_layout.addWidget(self.connect_btn)

        # Separator
        main_layout.addWidget(self.create_separator())

        # Settings section
        settings_group = self.create_settings_section()
        main_layout.addWidget(settings_group)

        # Server selection
        server_group = self.create_server_section()
        main_layout.addWidget(server_group)

        # Separator
        main_layout.addWidget(self.create_separator())

        # Activity log
        log_group = self.create_log_section()
        main_layout.addWidget(log_group)

        # Stretch to push everything up
        main_layout.addStretch()

        # System tray icon (optional)
        self.setup_system_tray()

    def create_title_section(self) -> QHBoxLayout:
        """Create title section"""
        layout = QHBoxLayout()

        title = QLabel("TS PROTECTOR PRO")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        return layout

    def create_status_section(self) -> QVBoxLayout:
        """Create status display section"""
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Status indicator and text
        status_layout = QHBoxLayout()

        self.status_indicator = QLabel()
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setProperty("status", "disconnected")
        self.status_indicator.setFixedSize(12, 12)

        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setObjectName("statusLabel")

        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # IP address
        self.ip_label = QLabel("Your IP: Loading...")
        self.ip_label.setObjectName("ipLabel")

        layout.addLayout(status_layout)
        layout.addWidget(self.ip_label)

        return layout

    def create_connect_button(self) -> QPushButton:
        """Create the main connect/disconnect button"""
        btn = QPushButton("CONNECT")
        btn.setObjectName("connectButton")
        btn.setProperty("connected", False)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.on_connect_button_clicked)
        return btn

    def create_settings_section(self) -> QGroupBox:
        """Create settings section"""
        group = QGroupBox("Settings")
        layout = QVBoxLayout()

        # Auto-detect TeamSpeak
        self.auto_detect_cb = QCheckBox("Auto-detect TeamSpeak")
        self.auto_detect_cb.setChecked(True)
        self.auto_detect_cb.stateChanged.connect(
            lambda state: self.auto_detect_changed.emit(state == Qt.CheckState.Checked.value)
        )

        # Start with Windows
        self.start_windows_cb = QCheckBox("Start with Windows")
        self.start_windows_cb.stateChanged.connect(
            lambda state: self.start_with_windows_changed.emit(state == Qt.CheckState.Checked.value)
        )

        # Minimize to tray
        self.minimize_tray_cb = QCheckBox("Minimize to tray")
        self.minimize_tray_cb.stateChanged.connect(
            lambda state: self.minimize_to_tray_changed.emit(state == Qt.CheckState.Checked.value)
        )

        layout.addWidget(self.auto_detect_cb)
        layout.addWidget(self.start_windows_cb)
        layout.addWidget(self.minimize_tray_cb)

        group.setLayout(layout)
        return group

    def create_server_section(self) -> QGroupBox:
        """Create server selection section"""
        group = QGroupBox("Server Settings")
        layout = QVBoxLayout()

        # Server dropdown
        server_layout = QHBoxLayout()
        server_label = QLabel("Region:")
        self.server_combo = QComboBox()
        self.server_combo.addItems([
            "US East",
            "US West",
            "Europe",
            "Asia"
        ])
        self.server_combo.currentTextChanged.connect(self.server_changed.emit)

        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_combo, 1)

        # Ping display
        ping_layout = QHBoxLayout()
        ping_label = QLabel("Ping:")
        self.ping_label = QLabel("-- ms")

        ping_layout.addWidget(ping_label)
        ping_layout.addWidget(self.ping_label)
        ping_layout.addStretch()

        layout.addLayout(server_layout)
        layout.addLayout(ping_layout)

        group.setLayout(layout)
        return group

    def create_log_section(self) -> QGroupBox:
        """Create activity log section"""
        group = QGroupBox("Activity Log")
        layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setPlaceholderText("Application logs will appear here...")

        layout.addWidget(self.log_text)
        group.setLayout(layout)
        return group

    def create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def load_stylesheet(self):
        """Load the QSS stylesheet"""
        style_path = Path(__file__).parent / "styles.qss"
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())

    def on_connect_button_clicked(self):
        """Handle connect button click"""
        if self.is_connected:
            self.disconnect_clicked.emit()
        else:
            self.connect_clicked.emit()

    def update_connection_status(self, connected: bool):
        """Update UI based on connection status"""
        self.is_connected = connected

        if connected:
            self.connect_btn.setText("DISCONNECT")
            self.connect_btn.setProperty("connected", True)
            self.status_label.setText("Status: Connected")
            self.status_indicator.setProperty("status", "connected")
        else:
            self.connect_btn.setText("CONNECT")
            self.connect_btn.setProperty("connected", False)
            self.status_label.setText("Status: Disconnected")
            self.status_indicator.setProperty("status", "disconnected")

        # Refresh stylesheet
        self.connect_btn.style().unpolish(self.connect_btn)
        self.connect_btn.style().polish(self.connect_btn)
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)

    def update_ip_address(self, ip: str):
        """Update displayed IP address"""
        self.ip_label.setText(f"Your IP: {ip}")

    def update_ping(self, ping_ms: int):
        """Update displayed ping"""
        if ping_ms >= 0:
            self.ping_label.setText(f"{ping_ms} ms")
        else:
            self.ping_label.setText("-- ms")

    def append_log(self, message: str, level: str = "INFO"):
        """Append message to activity log"""
        # Color based on level
        colors = {
            "INFO": "#58a6ff",
            "SUCCESS": "#3fb950",
            "WARNING": "#d29922",
            "ERROR": "#f85149"
        }

        color = colors.get(level, "#c9d1d9")
        html = f'<span style="color: {color};">{message}</span>'

        self.log_text.append(html)

        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def load_settings(self, settings: dict):
        """Load settings into UI"""
        self.auto_detect_cb.setChecked(settings.get("auto_detect", True))
        self.start_windows_cb.setChecked(settings.get("start_with_windows", False))
        self.minimize_tray_cb.setChecked(settings.get("minimize_to_tray", False))

        server = settings.get("selected_server", "us-east")
        server_map = {
            "us-east": "US East",
            "us-west": "US West",
            "eu": "Europe",
            "asia": "Asia"
        }
        self.server_combo.setCurrentText(server_map.get(server, "US East"))

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def closeEvent(self, event):
        """Handle window close event"""
        if self.minimize_tray_cb.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "TS Protector Pro",
                "Application minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()
