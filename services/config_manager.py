"""Configuration management service."""

import json
from pathlib import Path
from typing import Optional

from models import UserConfig
from services.path_manager import PathManager


class ConfigManager:
    """Manages user configuration persistence."""

    def __init__(self, path_manager: PathManager):
        """Initialize config manager.

        Args:
            path_manager: Path manager instance
        """
        self.path_manager = path_manager
        self._config: Optional[UserConfig] = None

    @property
    def config(self) -> UserConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self._config = self.load()
        return self._config

    def load(self) -> UserConfig:
        """Load configuration from disk.

        On first startup (when config file doesn't exist), this will attempt to
        auto-detect Audio for VATSIM at its default installation location and
        populate the afv_path setting automatically.

        Returns:
            UserConfig instance (default if file doesn't exist)
        """
        config_file = self.path_manager.config_file

        if not config_file.exists():
            config = UserConfig()

            default_afv_path = Path(r"C:\AudioForVATSIM\AudioForVATSIM.exe")
            if default_afv_path.exists():
                config.afv_path = str(default_afv_path)
                print(f"Auto-detected Audio for VATSIM at {default_afv_path}")

                self._config = config
                self.save(config)

            return config

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserConfig.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading config: {e}")
            return UserConfig()

    def save(self, config: Optional[UserConfig] = None) -> None:
        """Save configuration to disk.

        Args:
            config: Configuration to save. Uses current config if None.
        """
        if config is not None:
            self._config = config

        if self._config is None:
            return

        self.path_manager.config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.path_manager.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config.to_dict(), f, indent=2)
        except (OSError, TypeError) as e:
            print(f"Error saving config: {e}")

    def update(self, **kwargs) -> None:
        """Update configuration fields and save.

        Args:
            **kwargs: Fields to update
        """
        config = self.config
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save(config)
