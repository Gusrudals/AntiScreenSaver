"""
Configuration management for Anti-Screensaver Mouse Mover

This module handles loading, saving, and validating user configuration.
Configuration is stored as JSON in the platform-specific config directory.
"""

import json
import shutil
from pathlib import Path
from typing import Optional
from .contracts import IConfigurationManager
from .models import Configuration, RunningState
from .exceptions import ConfigurationError
from ..platform import get_config_file_path, ensure_config_dir


class JsonConfigurationManager(IConfigurationManager):
    """
    JSON-based configuration manager.

    Handles configuration persistence using JSON format with atomic writes
    and automatic backup/recovery for corrupted files.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional custom config file path (for testing)
        """
        self._config_path = config_path or get_config_file_path()

    def load(self) -> Configuration:
        """
        Load configuration from disk.

        Returns:
            Configuration object with user settings

        Raises:
            ConfigurationError: If config is corrupted beyond recovery
        """
        # Ensure config directory exists
        try:
            ensure_config_dir()
        except OSError as e:
            raise ConfigurationError(f"Cannot create config directory: {e}")

        # If config file doesn't exist, create default
        if not self._config_path.exists():
            default_config = self.create_default()
            self.save(default_config)
            return default_config

        # Try to load existing config
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert string state to enum
            last_state_str = data.get('last_state', 'stopped')
            last_state = (RunningState.RUNNING if last_state_str == 'running'
                          else RunningState.STOPPED)

            config = Configuration(
                interval_seconds=data.get('interval_seconds', 30),
                auto_start=data.get('auto_start', False),
                last_state=last_state,
                version=data.get('version', '1.0.0')
            )

            # Validate loaded config
            errors = config.validate()
            if errors:
                # Config is invalid - backup and create new default
                backup_path = self._config_path.with_suffix('.json.bak')
                shutil.copy2(self._config_path, backup_path)
                default_config = self.create_default()
                self.save(default_config)
                raise ConfigurationError(
                    f"Invalid configuration (backed up to {backup_path}): {', '.join(errors)}"
                )

            return config

        except json.JSONDecodeError as e:
            # Corrupted JSON - backup and create new default
            backup_path = self._config_path.with_suffix('.json.bak')
            shutil.copy2(self._config_path, backup_path)
            default_config = self.create_default()
            self.save(default_config)
            raise ConfigurationError(
                f"Corrupted config file (backed up to {backup_path}): {e}"
            )

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def save(self, config: Configuration) -> None:
        """
        Save configuration to disk with atomic write.

        Args:
            config: Configuration object to persist

        Raises:
            ConfigurationError: If unable to write to disk
        """
        # Validate before saving
        errors = config.validate()
        if errors:
            raise ConfigurationError(f"Cannot save invalid configuration: {', '.join(errors)}")

        # Prepare data for JSON serialization
        data = {
            'interval_seconds': config.interval_seconds,
            'auto_start': config.auto_start,
            'last_state': config.last_state.value,  # Convert enum to string
            'version': config.version
        }

        # Atomic write: write to temp file, then rename
        temp_path = self._config_path.with_suffix('.json.tmp')
        try:
            # Ensure directory exists
            ensure_config_dir()

            # Write to temporary file with pretty formatting
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic rename (replaces existing file)
            temp_path.replace(self._config_path)

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise ConfigurationError(f"Failed to save configuration: {e}")

    def get_config_path(self) -> str:
        """
        Get platform-specific configuration file path.

        Returns:
            Absolute path to config file
        """
        return str(self._config_path.absolute())

    def create_default(self) -> Configuration:
        """
        Create default configuration.

        Returns:
            Configuration with default values
        """
        return Configuration(
            interval_seconds=30,
            auto_start=False,
            last_state=RunningState.STOPPED,
            version="1.0.0"
        )
