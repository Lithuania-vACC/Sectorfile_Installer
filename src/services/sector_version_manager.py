"""Sectorfile version management service.

This module handles checking and comparing sectorfile versions from AeroNav GNG.

Version Format:
    Sectorfile versions follow the format: YYYYMMDDHHMMSS-AIRAC-BUILD
    - YYYYMMDDHHMMSS: Timestamp of the sectorfile package (e.g., 20251004190612)
    - AIRAC: AIRAC cycle (e.g., 251001 for cycle 2510, revision 01)
    - BUILD: Build number padded to 4 digits (e.g., 0003)

    Example: 20251004190612-251001-0003
"""

from typing import Optional

import requests
from bs4 import BeautifulSoup

from config.settings import settings
from services.path_manager import PathManager


class SectorVersionManager:
    """Manages sectorfile version checking and comparison."""

    @staticmethod
    def get_current_version() -> str:
        """Get the currently installed sectorfile version.

        Returns:
            Version string in format YYYYMMDDHHMMSS-AIRAC-BUILD

        Raises:
            FileNotFoundError: If no .SCT file is found in the sectorfile directory
        """
        sectorfile_dir = PathManager().sectorfile
        sct_files = list(sectorfile_dir.glob("*.SCT"))

        if not sct_files:
            raise FileNotFoundError("No .SCT file found in sectorfile directory.")

        sct_file = sct_files[0]
        version = sct_file.stem.split("_")[-1]

        return version

    @staticmethod
    def get_newest_version() -> str:
        """Fetch the newest available sectorfile version from AeroNav GNG.

        Scrapes the AeroNav GNG page to find the latest sectorfile package.
        The version is constructed from the timestamp, AIRAC cycle, and build number
        found in the HTML table.

        Returns:
            Version string in format YYYYMMDDHHMMSS-AIRAC-BUILD

        Raises:
            ConnectionError: If the AeroNav page cannot be fetched
            ValueError: If no valid sectorfile versions are found
        """
        url = f"{settings.AERONAV_BASE_URL}/{settings.FIR_CODE}"
        response = requests.get(url)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch sectorfile versions from {url}")

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr")
        newest_version: Optional[str] = None
        newest_timestamp = 0

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            package_name = cols[1].text.strip()
            if package_name != f"{settings.FIR_CODE} Installer":
                continue

            timestamp_str = cols[4].text.strip()
            timestamp = int(
                timestamp_str.replace("zip", "")
                .replace("7z", "")
                .replace(":", "")
                .replace("-", "")
                .replace(" ", "")
            )

            if timestamp > newest_timestamp:
                newest_timestamp = timestamp

                airac = cols[2].text.strip().replace(" / ", "")

                build = cols[3].text.strip().zfill(4)

                newest_version = f"{timestamp}-{airac}-{build}"

        if not newest_version:
            raise ValueError(f"No valid sectorfile versions found for {settings.FIR_CODE}")

        return newest_version

    @staticmethod
    def is_update_available() -> bool:
        """Check if a newer sectorfile version is available online.

        Compares the currently installed version with the newest available version
        by comparing their AIRAC cycle numbers.

        Returns:
            True if a newer version is available, False otherwise
        """
        try:
            current_version = SectorVersionManager.get_current_version()
            current_date = int(current_version.split("-")[0])

            newest_version = SectorVersionManager.get_newest_version()
            newest_date = int(newest_version.split("-")[0])

            return current_date < newest_date

        except Exception as e:
            print(f"Error checking for sectorfile update: {e}")
            return False
