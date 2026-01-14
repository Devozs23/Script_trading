"""
Process Monitor for TeamSpeak auto-detection
Monitors running processes and triggers VPN connection/disconnection
"""
import psutil
import logging
import threading
import time
from typing import Callable, List, Optional


class ProcessMonitor:
    """Monitors system processes for TeamSpeak instances"""

    TEAMSPEAK_PROCESSES = [
        "ts3client_win64.exe",
        "ts3client_win32.exe",
        "ts3client.exe",
        "TeamSpeak.exe"
    ]

    def __init__(self, check_interval: int = 5):
        """
        Initialize the process monitor

        Args:
            check_interval: Seconds between process checks
        """
        self.logger = logging.getLogger(__name__)
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.teamspeak_running = False

        # Callbacks
        self.on_teamspeak_started: Optional[Callable] = None
        self.on_teamspeak_stopped: Optional[Callable] = None

    def is_teamspeak_running(self) -> bool:
        """
        Check if TeamSpeak is currently running

        Returns:
            bool: True if any TeamSpeak process is found
        """
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and proc_name in self.TEAMSPEAK_PROCESSES:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            return False

        except Exception as e:
            self.logger.error(f"Error checking processes: {str(e)}")
            return False

    def _monitor_loop(self):
        """Main monitoring loop running in separate thread"""
        self.logger.info("Process monitoring started")

        while self.monitoring:
            try:
                current_state = self.is_teamspeak_running()

                # State change detection
                if current_state and not self.teamspeak_running:
                    # TeamSpeak just started
                    self.logger.info("TeamSpeak process detected")
                    self.teamspeak_running = True
                    if self.on_teamspeak_started:
                        self.on_teamspeak_started()

                elif not current_state and self.teamspeak_running:
                    # TeamSpeak just stopped
                    self.logger.info("TeamSpeak process stopped")
                    self.teamspeak_running = False
                    if self.on_teamspeak_stopped:
                        self.on_teamspeak_stopped()

                # Wait before next check
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitor loop: {str(e)}")
                time.sleep(self.check_interval)

        self.logger.info("Process monitoring stopped")

    def start_monitoring(self) -> bool:
        """
        Start monitoring TeamSpeak processes

        Returns:
            bool: True if monitoring started successfully
        """
        if self.monitoring:
            self.logger.warning("Monitoring is already active")
            return False

        self.monitoring = True
        self.teamspeak_running = self.is_teamspeak_running()  # Initial state

        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("Process monitoring initialized")
        return True

    def stop_monitoring(self):
        """Stop monitoring TeamSpeak processes"""
        if not self.monitoring:
            return

        self.logger.info("Stopping process monitoring...")
        self.monitoring = False

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=self.check_interval + 1)

        self.logger.info("Process monitoring stopped")

    def set_callbacks(self, on_started: Callable = None, on_stopped: Callable = None):
        """
        Set callback functions for TeamSpeak state changes

        Args:
            on_started: Called when TeamSpeak starts
            on_stopped: Called when TeamSpeak stops
        """
        self.on_teamspeak_started = on_started
        self.on_teamspeak_stopped = on_stopped
