"""Sectorfile version management service.

This module handles checking and comparing sectorfile versions from AeroNav GNG.

Version Format:
    Sectorfile versions follow the format: YYYYMMDDHHMMSS-AIRAC-BUILD
    - YYYYMMDDHHMMSS: Timestamp of the sectorfile package (e.g., 20251004190612)
    - AIRAC: AIRAC cycle (e.g., 251001 for cycle 2510, revision 01)
    - BUILD: Build number padded to 4 digits (e.g., 0003)

    Example: 20251004190612-251001-0003
"""

import re
from typing import Optional

import requests

from config import settings
from services import PathManager


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

        html = response.text
        newest_version: Optional[str] = None
        newest_timestamp = 0

        # Pattern to match table rows with their td cells
        # Captures content of td cells in a row
        row_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
        td_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)

        for row_match in row_pattern.finditer(html):
            row_html = row_match.group(1)
            cells = [td_pattern.sub(lambda m: m.group(1), cell)
                    for cell in td_pattern.findall(row_html)]

            if len(cells) < 5:
                continue

            cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]

            package_name = cells[1]
            if package_name != f"{settings.FIR_CODE} Installer":
                continue

            timestamp_str = cells[4]
            timestamp = int(
                timestamp_str.replace("zip", "")
                .replace("7z", "")
                .replace(":", "")
                .replace("-", "")
                .replace(" ", "")
            )

            if timestamp > newest_timestamp:
                newest_timestamp = timestamp

                airac = cells[2].replace(" / ", "")

                build = cells[3].zfill(4)

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
