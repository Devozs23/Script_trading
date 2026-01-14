"""
Settings manager for persistent configuration
Handles loading, saving, and managing application settings
"""
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict


class Settings:
    """Manages application settings with JSON persistence"""

    DEFAULT_SETTINGS = {
        "auto_detect": True,
        "start_with_windows": False,
        "minimize_to_tray": False,
        "selected_server": "us-east",
        "last_known_ip": "",
        "check_interval": 5,
        "auto_connect": True
    }

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize settings manager

        Args:
            config_file: Name of the configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = self._get_config_path(config_file)
        self.settings: Dict[str, Any] = {}
        self.load_settings()

    def _get_config_path(self, filename: str) -> Path:
        """
        Get the appropriate config file path based on OS

        Args:
            filename: Name of config file

        Returns:
            Path: Full path to config file
        """
        if sys.platform == "win32":
            # Windows: Use %APPDATA%
            app_data = Path.home() / "AppData" / "Roaming" / "TSProtectorPro"
        else:
            # Linux/Mac: Use ~/.config
            app_data = Path.home() / ".config" / "TSProtectorPro"

        # Create directory if it doesn't exist
        app_data.mkdir(parents=True, exist_ok=True)

        return app_data / filename

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from JSON file

        Returns:
            Dict: Loaded settings
        """
        if not self.config_path.exists():
            self.logger.info("Config file not found, using defaults")
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.save_settings()
            return self.settings

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            # Merge with defaults to ensure all keys exist
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.settings.update(loaded)

            self.logger.info(f"Settings loaded from {self.config_path}")
            return self.settings

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse config: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
            return self.settings

        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
            return self.settings

    def save_settings(self, new_settings: Dict[str, Any] = None) -> bool:
        """
        Save settings to JSON file

        Args:
            new_settings: Optional dict to merge with current settings

        Returns:
            bool: True if saved successfully
        """
        if new_settings:
            self.settings.update(new_settings)

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)

            self.logger.info(f"Settings saved to {self.config_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any, save: bool = True):
        """
        Set a setting value

        Args:
            key: Setting key
            value: New value
            save: Whether to save to disk immediately
        """
        self.settings[key] = value
        if save:
            self.save_settings()

    def add_to_startup(self) -> bool:
        """
        Add application to Windows startup

        Returns:
            bool: True if successful
        """
        if sys.platform != "win32":
            self.logger.warning("Startup registration only supported on Windows")
            return False

        try:
            import winreg
            import sys

            # Get executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = f'"{sys.executable}" "{Path(__file__).parent.parent / "main.py"}"'

            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )

            # Set value
            winreg.SetValueEx(key, "TSProtectorPro", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)

            self.logger.info("Added to Windows startup")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add to startup: {e}")
            return False

    def remove_from_startup(self) -> bool:
        """
        Remove application from Windows startup

        Returns:
            bool: True if successful
        """
        if sys.platform != "win32":
            return False

        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )

            winreg.DeleteValue(key, "TSProtectorPro")
            winreg.CloseKey(key)

            self.logger.info("Removed from Windows startup")
            return True

        except FileNotFoundError:
            # Key doesn't exist, already removed
            return True

        except Exception as e:
            self.logger.error(f"Failed to remove from startup: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to defaults

        Returns:
            bool: True if successful
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save_settings()
