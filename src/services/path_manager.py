"""Path management service."""

from pathlib import Path
from typing import List

from config.settings import settings


class PathManager:
    """Manages all application paths."""

    def __init__(self, root: Path | None = None):
        """Initialize path manager.

        Args:
            root: Root directory for the application. Defaults to current working directory.
        """
        self.root = root or Path.cwd()

    @property
    def temp(self) -> Path:
        """Get temp directory path."""
        return self.root / settings.TEMP_DIR

    @property
    def config_file(self) -> Path:
        """Get config file path."""
        return self.root / settings.CONFIG_FILE

    @property
    def euroscope(self) -> Path:
        """Get EuroScope directory path."""
        return self.root / settings.EUROSCOPE_DIR

    @property
    def sectorfile(self) -> Path:
        """Get sectorfile directory path."""
        return self.root / settings.SECTORFILE_DIR

    @property
    def custom_files(self) -> Path:
        """Get custom files directory path."""
        return self.root / settings.CUSTOM_FILES_DIR

    @property
    def assets(self) -> Path:
        """Get assets directory path."""
        return self.root / settings.ASSETS_DIR

    def custom_fir_path(self, fir_code: str) -> Path:
        """Get custom files path for a specific FIR.

        Args:
            fir_code: FIR code (e.g., 'EYVL')

        Returns:
            Path to custom FIR directory
        """
        return self.custom_files / fir_code

    def ensure_base_directories(self) -> None:
        """Create base directories if they don't exist."""
        self.temp.mkdir(parents=True, exist_ok=True)
        self.custom_files.mkdir(parents=True, exist_ok=True)
        self.assets.mkdir(parents=True, exist_ok=True)

    def ensure_fir_directories(self, fir_code: str) -> None:
        """Create FIR-specific directories if they don't exist.

        Args:
            fir_code: FIR code (e.g., 'EYVL')
        """
        fir_path = self.custom_fir_path(fir_code)
        fir_path.mkdir(parents=True, exist_ok=True)

        subdirs = ["Alias", "ASR", "Plugins", "Settings", "Sounds"]
        for subdir in subdirs:
            (fir_path / subdir).mkdir(parents=True, exist_ok=True)

    def get_profile_files(self) -> List[Path]:
        """Get all .prf files in the sectorfile directory.

        Returns:
            List of profile file paths
        """
        if not self.sectorfile.exists():
            return []
        return list(self.sectorfile.glob("*.prf"))
