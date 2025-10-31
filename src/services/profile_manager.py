"""EuroScope profile management service."""

from pathlib import Path
from typing import List


class ProfileManager:
    """Manages EuroScope profile (.prf) files."""

    @staticmethod
    def get_available_profiles(sectorfile_path: Path) -> List[str]:
        """Get list of available profile names.

        Args:
            sectorfile_path: Path to sectorfile directory

        Returns:
            List of profile names (without .prf extension)
        """
        if not sectorfile_path.exists():
            return []

        profiles = [prf_file.stem for prf_file in sectorfile_path.glob("*.prf")]

        return sorted(profiles)
