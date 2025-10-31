"""Application settings and configuration."""

import os
import tempfile
from dataclasses import dataclass


@dataclass
class Settings:
    """Global application settings."""

    APP_NAME: str = "vACC Lithuania"
    APP_VERSION: str = "2.1.5"
    FIR_CODE: str = "EYVL"

    TEMP_DIR: str = "temp"
    CONFIG_FILE: str = "config.json"
    EUROSCOPE_DIR: str = "Euroscope"
    SECTORFILE_DIR: str = "Sectorfile"
    CUSTOM_FILES_DIR: str = "Customfiles"
    ASSETS_DIR: str = "assets"

    WINDOW_WIDTH: int = 640
    WINDOW_HEIGHT: int = 380

    EUROSCOPE_MSI_URL: str = "https://euroscope.hu/install/EuroScopeSetup.3.2.3.2.msi"
    EUROSCOPE_FONT_NAME: str = "EuroScope.ttf"
    EUROSCOPE_FONT_PATH: str = "C:/Windows/Fonts/EuroScope.ttf"
    EUROSCOPE_FOLDER_NAME_MAP = {
        "_635FE19FDC6F4CF2866FC8696C8E5A0E": "soundbackends",
        "_E7043CA494204E24ABEE6401A7892467": "sounds",
    }

    AERONAV_BASE_URL: str = "https://files.aero-nav.com"
    SECTORFILE_DOWNLOAD_TIMEOUT: int = 300  # seconds (5 minutes)

    GITHUB_REPO_OWNER: str = "Lithuania-vACC"
    GITHUB_REPO_NAME: str = "Sectorfile_Installer"
    GITHUB_API_BASE: str = "https://api.github.com"
    UPDATE_ASSET_NAME: str = "main.dist.zip"
    UPDATE_TEMP_DIR: str = os.path.join(tempfile.gettempdir(), "sectorfile_installer_update")


settings = Settings()
