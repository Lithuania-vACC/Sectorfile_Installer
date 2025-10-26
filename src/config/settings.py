"""Application settings and configuration."""

from dataclasses import dataclass


@dataclass
class Settings:
    """Global application settings."""

    APP_NAME: str = "vACC Lithuania"

    FIR_CODE: str = "EYVL"

    TEMP_DIR: str = "temp"
    CONFIG_FILE: str = "config.json"
    EUROSCOPE_DIR: str = "Euroscope"
    SECTORFILE_DIR: str = "Sectorfile"
    CUSTOM_FILES_DIR: str = "Customfiles"
    ASSETS_DIR: str = "assets"

    WINDOW_WIDTH: int = 640
    WINDOW_HEIGHT: int = 380


# Global settings instance
settings = Settings()
