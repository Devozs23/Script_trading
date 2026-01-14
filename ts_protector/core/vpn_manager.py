"""
VPN Manager for Cloudflare WARP integration
Handles VPN connection, disconnection, and status monitoring
"""
import subprocess
import logging
from typing import Optional, Tuple
from pathlib import Path


class VPNManager:
    """Manages Cloudflare WARP VPN connections"""

    WARP_CLI_PATHS = [
        Path(r"C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe"),
        Path(r"C:\Program Files (x86)\Cloudflare\Cloudflare WARP\warp-cli.exe"),
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.warp_cli_path: Optional[Path] = None
        self._find_warp_cli()

    def _find_warp_cli(self) -> bool:
        """Locate the WARP CLI executable"""
        for path in self.WARP_CLI_PATHS:
            if path.exists():
                self.warp_cli_path = path
                self.logger.info(f"Found WARP CLI at: {path}")
                return True

        self.logger.warning("WARP CLI not found in standard locations")
        return False

    def is_warp_installed(self) -> bool:
        """Check if Cloudflare WARP is installed"""
        return self.warp_cli_path is not None and self.warp_cli_path.exists()

    def connect(self) -> Tuple[bool, str]:
        """
        Activate Cloudflare WARP VPN

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_warp_installed():
            return False, "WARP is not installed. Please install Cloudflare WARP first."

        try:
            self.logger.info("Attempting to connect to WARP...")
            result = subprocess.run(
                [str(self.warp_cli_path), 'connect'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info("Successfully connected to WARP")
                return True, "Connected successfully"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                self.logger.error(f"Failed to connect: {error_msg}")
                return False, f"Connection failed: {error_msg}"

        except subprocess.TimeoutExpired:
            self.logger.error("Connection timeout")
            return False, "Connection timeout. Please try again."
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return False, f"Error: {str(e)}"

    def disconnect(self) -> Tuple[bool, str]:
        """
        Deactivate Cloudflare WARP VPN

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_warp_installed():
            return False, "WARP is not installed"

        try:
            self.logger.info("Attempting to disconnect from WARP...")
            result = subprocess.run(
                [str(self.warp_cli_path), 'disconnect'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info("Successfully disconnected from WARP")
                return True, "Disconnected successfully"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                self.logger.error(f"Failed to disconnect: {error_msg}")
                return False, f"Disconnection failed: {error_msg}"

        except subprocess.TimeoutExpired:
            self.logger.error("Disconnection timeout")
            return False, "Disconnection timeout. Please try again."
        except Exception as e:
            self.logger.error(f"Disconnection error: {str(e)}")
            return False, f"Error: {str(e)}"

    def get_status(self) -> str:
        """
        Get current WARP connection status

        Returns:
            str: "Connected", "Disconnected", or "Unknown"
        """
        if not self.is_warp_installed():
            return "Not Installed"

        try:
            result = subprocess.run(
                [str(self.warp_cli_path), 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout.strip().lower()

            if 'connected' in output:
                return "Connected"
            elif 'disconnected' in output or 'disconnecting' in output:
                return "Disconnected"
            else:
                return "Unknown"

        except Exception as e:
            self.logger.error(f"Status check error: {str(e)}")
            return "Unknown"

    def is_connected(self) -> bool:
        """Check if currently connected to WARP"""
        return self.get_status() == "Connected"
