"""
System utilities for Windows integration
Handles WARP installation checks, downloads, and system tray
"""
import sys
import subprocess
import logging
import urllib.request
from pathlib import Path
from typing import Optional, Tuple


class SystemUtils:
    """System-level utility functions"""

    WARP_INSTALLER_URL = "https://1.1.1.1/Cloudflare_WARP_Release-x64.msi"
    WARP_CLI_PATHS = [
        Path(r"C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe"),
        Path(r"C:\Program Files (x86)\Cloudflare\Cloudflare WARP\warp-cli.exe"),
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_warp_installed(self) -> Tuple[bool, Optional[Path]]:
        """
        Check if Cloudflare WARP is installed

        Returns:
            Tuple[bool, Path]: (is_installed, path_to_cli)
        """
        for path in self.WARP_CLI_PATHS:
            if path.exists():
                self.logger.info(f"WARP found at: {path}")
                return True, path

        self.logger.warning("WARP CLI not found")
        return False, None

    def download_warp_installer(self, dest_path: Path = None) -> Optional[Path]:
        """
        Download WARP installer

        Args:
            dest_path: Destination path (None for temp directory)

        Returns:
            Path: Path to downloaded installer or None
        """
        if dest_path is None:
            import tempfile
            dest_path = Path(tempfile.gettempdir()) / "Cloudflare_WARP_Installer.msi"

        try:
            self.logger.info(f"Downloading WARP installer from {self.WARP_INSTALLER_URL}")

            # Download with progress
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(100, (downloaded / total_size) * 100)
                self.logger.debug(f"Download progress: {percent:.1f}%")

            urllib.request.urlretrieve(
                self.WARP_INSTALLER_URL,
                dest_path,
                reporthook=report_progress
            )

            self.logger.info(f"WARP installer downloaded to: {dest_path}")
            return dest_path

        except Exception as e:
            self.logger.error(f"Failed to download WARP installer: {e}")
            return None

    def install_warp(self, installer_path: Path = None) -> bool:
        """
        Install Cloudflare WARP

        Args:
            installer_path: Path to installer (will download if None)

        Returns:
            bool: True if installation successful
        """
        if sys.platform != "win32":
            self.logger.error("WARP installation only supported on Windows")
            return False

        # Download installer if not provided
        if installer_path is None or not installer_path.exists():
            installer_path = self.download_warp_installer()
            if not installer_path:
                return False

        try:
            self.logger.info("Starting WARP installation...")

            # Run silent installation
            result = subprocess.run(
                ['msiexec', '/i', str(installer_path), '/quiet', '/norestart'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                self.logger.info("WARP installed successfully")
                return True
            else:
                self.logger.error(f"Installation failed with code {result.returncode}")
                self.logger.error(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Installation timeout")
            return False

        except Exception as e:
            self.logger.error(f"Installation error: {e}")
            return False

    def is_admin(self) -> bool:
        """
        Check if running with administrator privileges

        Returns:
            bool: True if admin
        """
        if sys.platform != "win32":
            return False

        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def run_as_admin(self, script_path: str = None):
        """
        Restart the application with administrator privileges

        Args:
            script_path: Path to script (uses sys.executable if None)
        """
        if sys.platform != "win32":
            return

        try:
            import ctypes

            if script_path is None:
                script_path = sys.executable

            # Request elevation
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )

        except Exception as e:
            self.logger.error(f"Failed to elevate privileges: {e}")

    def get_app_version(self) -> str:
        """
        Get application version

        Returns:
            str: Version string
        """
        return "1.0.0"

    def get_system_info(self) -> dict:
        """
        Get system information

        Returns:
            dict: System info
        """
        import platform

        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'is_admin': self.is_admin()
        }

    def open_url(self, url: str):
        """
        Open URL in default browser

        Args:
            url: URL to open
        """
        import webbrowser
        webbrowser.open(url)

    def open_file_location(self, file_path: Path):
        """
        Open file location in file explorer

        Args:
            file_path: Path to file
        """
        if sys.platform == "win32":
            subprocess.run(['explorer', '/select,', str(file_path)])
        elif sys.platform == "darwin":
            subprocess.run(['open', '-R', str(file_path)])
        else:
            subprocess.run(['xdg-open', str(file_path.parent)])
