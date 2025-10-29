"""Application settings and configuration."""

import os
import tempfile
from dataclasses import dataclass


@dataclass
class Settings:
    """Global application settings."""

    # Application Identity
    APP_NAME: str = "vACC Lithuania"
    APP_VERSION: str = "2.1.3"
    FIR_CODE: str = "EYVL"

    # Directory Structure
    TEMP_DIR: str = "temp"
    CONFIG_FILE: str = "config.json"
    EUROSCOPE_DIR: str = "Euroscope"
    SECTORFILE_DIR: str = "Sectorfile"
    CUSTOM_FILES_DIR: str = "Customfiles"
    ASSETS_DIR: str = "assets"

    # Window Settings
    WINDOW_WIDTH: int = 640
    WINDOW_HEIGHT: int = 380

    # EuroScope Installation
    EUROSCOPE_MSI_URL: str = "https://euroscope.hu/install/EuroScopeSetup.3.2.3.2.msi"
    EUROSCOPE_FONT_NAME: str = "EuroScope.ttf"
    EUROSCOPE_FONT_PATH: str = "C:/Windows/Fonts/EuroScope.ttf"

    # Sectorfile Installation
    AERONAV_BASE_URL: str = "https://files.aero-nav.com"
    SECTORFILE_DOWNLOAD_TIMEOUT: int = 300  # seconds (5 minutes)

    # Auto-Update Configuration
    GITHUB_REPO_OWNER: str = "Lithuania-vACC"
    GITHUB_REPO_NAME: str = "Sectorfile_Installer"
    GITHUB_API_BASE: str = "https://api.github.com"
    UPDATE_ASSET_NAME: str = "main.dist.zip"
    UPDATE_TEMP_DIR: str = os.path.join(tempfile.gettempdir(), "sectorfile_installer_update")


# Global settings instance
settings = Settings()
