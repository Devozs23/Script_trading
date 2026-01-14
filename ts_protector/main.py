"""
TS Protector Pro - Main Application Entry Point
Integrates all components and manages application lifecycle
"""
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

from core.vpn_manager import VPNManager
from core.process_monitor import ProcessMonitor
from core.settings import Settings
from core.logger import ActivityLogger
from ui.main_window import MainWindow
from utils.network import NetworkUtils
from utils.system import SystemUtils


class TSProtectorApp:
    """Main application class integrating all components"""

    def __init__(self):
        """Initialize the application"""
        # Initialize core components
        self.settings = Settings()
        self.logger = ActivityLogger()
        self.vpn_manager = VPNManager()
        self.process_monitor = ProcessMonitor(
            check_interval=self.settings.get("check_interval", 5)
        )
        self.network_utils = NetworkUtils()
        self.system_utils = SystemUtils()

        # Initialize UI
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("TS Protector Pro")
        self.window = MainWindow()

        # Setup connections
        self.setup_connections()

        # Setup logger callback
        self.logger.set_callback(self.on_log_message)

        # Initial checks
        self.perform_initial_checks()

        # Load user settings
        self.load_user_settings()

        # Setup periodic tasks
        self.setup_timers()

        self.logger.success("Application initialized successfully")

    def setup_connections(self):
        """Connect UI signals to handlers"""
        # Connect button
        self.window.connect_clicked.connect(self.on_connect_vpn)
        self.window.disconnect_clicked.connect(self.on_disconnect_vpn)

        # Settings
        self.window.auto_detect_changed.connect(self.on_auto_detect_changed)
        self.window.start_with_windows_changed.connect(self.on_start_with_windows_changed)
        self.window.minimize_to_tray_changed.connect(self.on_minimize_to_tray_changed)
        self.window.server_changed.connect(self.on_server_changed)

        # Process monitor callbacks
        self.process_monitor.set_callbacks(
            on_started=self.on_teamspeak_started,
            on_stopped=self.on_teamspeak_stopped
        )

    def setup_timers(self):
        """Setup periodic update timers"""
        # IP address update timer (every 30 seconds)
        self.ip_timer = QTimer()
        self.ip_timer.timeout.connect(self.update_ip_address)
        self.ip_timer.start(30000)

        # Ping test timer (every 10 seconds)
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.update_ping)
        self.ping_timer.start(10000)

        # Initial updates
        QTimer.singleShot(1000, self.update_ip_address)
        QTimer.singleShot(2000, self.update_ping)

    def perform_initial_checks(self):
        """Perform initial system checks"""
        # Check if WARP is installed
        if not self.vpn_manager.is_warp_installed():
            self.logger.warning("Cloudflare WARP is not installed")
            self.show_warp_install_dialog()
        else:
            self.logger.info("Cloudflare WARP detected")

        # Check VPN status
        status = self.vpn_manager.get_status()
        if status == "Connected":
            self.window.update_connection_status(True)
            self.logger.info("VPN is already connected")

    def show_warp_install_dialog(self):
        """Show dialog for WARP installation"""
        reply = QMessageBox.question(
            self.window,
            "WARP Not Installed",
            "Cloudflare WARP is not installed on your system.\n\n"
            "TS Protector Pro requires WARP to function.\n\n"
            "Would you like to download and install it now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.install_warp()

    def install_warp(self):
        """Install Cloudflare WARP"""
        self.logger.info("Starting WARP installation...")

        # Check admin privileges
        if not self.system_utils.is_admin():
            QMessageBox.warning(
                self.window,
                "Administrator Required",
                "Administrator privileges are required to install WARP.\n\n"
                "Please run this application as administrator."
            )
            return

        # Show progress message
        self.window.append_log("Downloading WARP installer...", "INFO")

        # Download and install (this should be done in a separate thread for production)
        success = self.system_utils.install_warp()

        if success:
            self.logger.success("WARP installed successfully")
            QMessageBox.information(
                self.window,
                "Installation Complete",
                "Cloudflare WARP has been installed successfully!\n\n"
                "Please restart the application."
            )
        else:
            self.logger.error("WARP installation failed")
            QMessageBox.critical(
                self.window,
                "Installation Failed",
                "Failed to install Cloudflare WARP.\n\n"
                "Please install it manually from:\nhttps://1.1.1.1"
            )

    def load_user_settings(self):
        """Load user settings and apply them"""
        settings_dict = self.settings.settings
        self.window.load_settings(settings_dict)

        # Start process monitoring if auto-detect is enabled
        if settings_dict.get("auto_detect", True):
            self.process_monitor.start_monitoring()
            self.logger.info("Process monitoring enabled")

    def on_connect_vpn(self):
        """Handle VPN connection request"""
        self.logger.info("Connecting to VPN...")
        self.window.append_log("Connecting to VPN...", "INFO")

        success, message = self.vpn_manager.connect()

        if success:
            self.logger.success("Connected to VPN successfully")
            self.window.update_connection_status(True)
            self.window.append_log("Connected successfully", "SUCCESS")
            self.update_ip_address()
        else:
            self.logger.error(f"Connection failed: {message}")
            self.window.append_log(f"Connection failed: {message}", "ERROR")
            QMessageBox.warning(self.window, "Connection Failed", message)

    def on_disconnect_vpn(self):
        """Handle VPN disconnection request"""
        self.logger.info("Disconnecting from VPN...")
        self.window.append_log("Disconnecting from VPN...", "INFO")

        success, message = self.vpn_manager.disconnect()

        if success:
            self.logger.success("Disconnected from VPN")
            self.window.update_connection_status(False)
            self.window.append_log("Disconnected successfully", "SUCCESS")
            self.update_ip_address()
        else:
            self.logger.error(f"Disconnection failed: {message}")
            self.window.append_log(f"Disconnection failed: {message}", "ERROR")

    def on_auto_detect_changed(self, enabled: bool):
        """Handle auto-detect setting change"""
        self.settings.set("auto_detect", enabled)

        if enabled:
            self.process_monitor.start_monitoring()
            self.logger.info("Auto-detection enabled")
            self.window.append_log("Auto-detection enabled", "INFO")
        else:
            self.process_monitor.stop_monitoring()
            self.logger.info("Auto-detection disabled")
            self.window.append_log("Auto-detection disabled", "INFO")

    def on_start_with_windows_changed(self, enabled: bool):
        """Handle start with Windows setting change"""
        self.settings.set("start_with_windows", enabled)

        if enabled:
            success = self.settings.add_to_startup()
            if success:
                self.logger.info("Added to Windows startup")
                self.window.append_log("Added to Windows startup", "SUCCESS")
        else:
            success = self.settings.remove_from_startup()
            if success:
                self.logger.info("Removed from Windows startup")
                self.window.append_log("Removed from Windows startup", "INFO")

    def on_minimize_to_tray_changed(self, enabled: bool):
        """Handle minimize to tray setting change"""
        self.settings.set("minimize_to_tray", enabled)
        self.logger.info(f"Minimize to tray: {enabled}")

    def on_server_changed(self, server_name: str):
        """Handle server selection change"""
        server_map = {
            "US East": "us-east",
            "US West": "us-west",
            "Europe": "eu",
            "Asia": "asia"
        }

        server_key = server_map.get(server_name, "us-east")
        self.settings.set("selected_server", server_key)
        self.logger.info(f"Selected server: {server_name}")
        self.update_ping()

    def on_teamspeak_started(self):
        """Handle TeamSpeak process detected"""
        self.logger.info("TeamSpeak detected - Auto-connecting to VPN")
        self.window.append_log("TeamSpeak detected", "INFO")

        if self.settings.get("auto_connect", True):
            self.on_connect_vpn()

    def on_teamspeak_stopped(self):
        """Handle TeamSpeak process stopped"""
        self.logger.info("TeamSpeak stopped - Auto-disconnecting from VPN")
        self.window.append_log("TeamSpeak stopped", "INFO")

        if self.settings.get("auto_connect", True):
            self.on_disconnect_vpn()

    def update_ip_address(self):
        """Update displayed IP address"""
        ip = self.network_utils.get_current_ip()
        if ip:
            self.window.update_ip_address(ip)
            self.settings.set("last_known_ip", ip)
        else:
            self.window.update_ip_address("Unable to detect")

    def update_ping(self):
        """Update displayed ping"""
        latency = self.network_utils.test_latency()
        if latency is not None:
            self.window.update_ping(latency)
        else:
            self.window.update_ping(-1)

    def on_log_message(self, message: str, level: str):
        """Callback for new log messages"""
        self.window.append_log(message, level)

    def run(self) -> int:
        """Run the application"""
        self.window.show()
        return self.app.exec()

    def cleanup(self):
        """Cleanup resources before exit"""
        self.logger.info("Application shutting down...")
        self.process_monitor.stop_monitoring()
        self.settings.save_settings()


def main():
    """Main entry point"""
    try:
        app = TSProtectorApp()
        exit_code = app.run()
        app.cleanup()
        sys.exit(exit_code)

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
