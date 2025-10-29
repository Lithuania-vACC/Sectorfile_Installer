"""Installation service for EuroScope and sectorfiles."""

import platform
import shutil
import subprocess
import time
import urllib.request
import webbrowser
import zipfile
from pathlib import Path
from typing import Callable, Optional

import pymsi

from config.settings import settings
from services.path_manager import PathManager


def extract_root(root, output: Path, is_root: bool = True):
    """Extract files from MSI root directory."""
    if not output.exists():
        output.mkdir(parents=True, exist_ok=True)

    for component in root.components.values():
        for file in component.files.values():
            if file.media is None:
                continue
            cab_file = file.resolve()
            (output / file.name).write_bytes(cab_file.decompress())

    for child in root.children.values():
        folder_name = child.name
        if is_root:
            if "." in child.id:
                folder_name, guid = child.id.split(".", 1)
                if child.id != folder_name:
                    print(f"Warning: Directory ID '{child.id}' has a GUID suffix ({guid}).")
            else:
                folder_name = child.id
        extract_root(child, output / folder_name, False)


class Installer:
    """Handles installation of EuroScope and sectorfiles."""

    def __init__(self, path_manager: PathManager):
        """Initialize installer.

        Args:
            path_manager: Path manager instance
        """
        self.path_manager = path_manager

    def install_euroscope(
        self, version: str, progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Install EuroScope from official MSI installer.

        Args:
            version: Version string to set after installation
            progress_callback: Optional callback for progress updates

        Returns:
            True if successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback("Preparing installation...")

            if self.path_manager.euroscope.exists():
                shutil.rmtree(self.path_manager.euroscope)

            self.path_manager.temp.mkdir(parents=True, exist_ok=True)

            if progress_callback:
                progress_callback("Downloading EuroScope MSI installer...")

            msi_path = self.path_manager.temp / "EuroScopeSetup.msi"
            msi_url = "https://euroscope.hu/install/EuroScopeSetup.3.2.3.1.msi"
            urllib.request.urlretrieve(msi_url, msi_path)

            if progress_callback:
                progress_callback("Extracting files from MSI...")

            package = pymsi.Package(msi_path)
            msi = pymsi.Msi(package, True)

            folders = []
            for media in msi.medias.values():
                if media.cabinet and media.cabinet.disks:
                    for disk in media.cabinet.disks.values():
                        for directory in disk:
                            for folder in directory.folders:
                                if folder not in folders:
                                    folders.append(folder)

            if progress_callback:
                progress_callback(f"Decompressing {len(folders)} folders...")

            for folder in folders:
                folder.decompress()

            self.path_manager.euroscope.mkdir(parents=True, exist_ok=True)

            if progress_callback:
                progress_callback("Extracting files...")

            extract_root(msi.root, self.path_manager.euroscope)

            package.close()
            msi_path.unlink(missing_ok=True)

            if progress_callback:
                progress_callback("Installing EuroScope font...")

            self._install_euroscope_font()

            if progress_callback:
                progress_callback("Installation complete!")

            return True

        except Exception as e:
            print(f"Error installing EuroScope: {e}")
            if progress_callback:
                progress_callback(f"Error: {e}")
            return False

    def _install_euroscope_font(self) -> None:
        """Install EuroScope.ttf font on Windows if it doesn't exist."""
        if platform.system() != "Windows":
            return

        system_font_path = Path("C:/Windows/Fonts/EuroScope.ttf")

        if system_font_path.exists():
            print("EuroScope font is already installed.")
            return

        try:
            source_font_path = self.path_manager.euroscope / "FontsFolder" / "EuroScope.ttf"

            if not source_font_path.exists():
                print(f"Warning: Font not found at {source_font_path}")
                return

            system_font_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_font_path, system_font_path)

            print("EuroScope font installed successfully.")

        except Exception as e:
            print(f"Warning: Could not install EuroScope font: {e}")

    def install_sectorfile(
        self, progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Open browser and file explorer for manual sectorfile download, then wait and extract.

        Since AeroNav requires authentication, the user must manually:
        1. Log in to AeroNav with Navigraph and VATSIM accounts
        2. Download the sectorfile package
        3. Place it in the Sectorfile folder
        4. This function will detect it and extract automatically

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            True if successful, False otherwise
        """
        try:
            self.path_manager.sectorfile.mkdir(parents=True, exist_ok=True)

            if progress_callback:
                progress_callback("Clearing sectorfile folder...")

            for item in self.path_manager.sectorfile.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

            aeronav_url = f"https://files.aero-nav.com/{settings.FIR_CODE}"
            webbrowser.open(aeronav_url)

            self._open_file_explorer(self.path_manager.sectorfile)

            if progress_callback:
                progress_callback("Waiting for zip file...")

            zip_file = self._wait_for_zip_file(progress_callback)

            if not zip_file:
                if progress_callback:
                    progress_callback("No zip file found or timeout")
                return False

            if progress_callback:
                progress_callback("Extracting sectorfile...")

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.path_manager.sectorfile)

            zip_file.unlink()

            if progress_callback:
                progress_callback("Sectorfile installation complete!")

            return True

        except Exception as e:
            print(f"Error installing sectorfile: {e}")
            if progress_callback:
                progress_callback(f"Error: {e}")
            return False

    def _wait_for_zip_file(
        self, progress_callback: Optional[Callable[[str], None]] = None, timeout: int = 300
    ) -> Optional[Path]:
        """Wait for a zip file to appear in the Sectorfile directory.

        Args:
            progress_callback: Optional callback for progress updates
            timeout: Maximum time to wait in seconds (default: 5 minutes)

        Returns:
            Path to the zip file if found, None if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            zip_files = list(self.path_manager.sectorfile.glob("*.zip"))

            if zip_files:
                return zip_files[0]

            elapsed = int(time.time() - start_time)
            if progress_callback and elapsed % 5 == 0:
                remaining = timeout - elapsed
                progress_callback(f"Waiting for zip file... ({remaining}s remaining)")

            time.sleep(1)

        return None

    def _open_file_explorer(self, path: Path) -> None:
        """Open directory in system file explorer.

        Args:
            path: Directory path to open
        """
        system = platform.system()

        try:
            if system == "Windows":
                subprocess.run(["explorer", str(path)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(path)])
        except Exception as e:
            print(f"Error opening file explorer: {e}")
