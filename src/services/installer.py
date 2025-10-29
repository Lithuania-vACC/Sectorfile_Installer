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

    FOLDER_NAME_MAP = {
        "_635FE19FDC6F4CF2866FC8696C8E5A0E": "soundbackends",
        "_E7043CA494204E24ABEE6401A7892467": "sounds",
    }

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
            # Check if this ID has a mapped name
            if child.id in FOLDER_NAME_MAP:
                folder_name = FOLDER_NAME_MAP[child.id]
            elif "." in child.id:
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
            urllib.request.urlretrieve(settings.EUROSCOPE_MSI_URL, msi_path)

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
                progress_callback("Copying AppData files to root...")

            self._copy_appdata_to_root()

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

    def _copy_appdata_to_root(self) -> None:
        """Copy all files and folders from AppDataFolder/Euroscope/ to the root directory."""
        try:
            appdata_source = self.path_manager.euroscope / "AppDataFolder" / "Euroscope"

            if not appdata_source.exists():
                print(f"Warning: AppDataFolder/Euroscope not found at {appdata_source}")
                return

            # Copy all contents from AppDataFolder/Euroscope/ to root
            for item in appdata_source.iterdir():
                dest = self.path_manager.euroscope / item.name

                if item.is_file():
                    shutil.copy2(item, dest)
                    print(f"Copied file: {item.name}")
                elif item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                    print(f"Copied directory: {item.name}")

            print("AppData files copied successfully.")

        except Exception as e:
            print(f"Warning: Could not copy AppData files: {e}")

    def _install_euroscope_font(self) -> None:
        """Install EuroScope.ttf font on Windows if it doesn't exist."""
        if platform.system() != "Windows":
            return

        system_font_path = Path(settings.EUROSCOPE_FONT_PATH)

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

            aeronav_url = f"{settings.AERONAV_BASE_URL}/{settings.FIR_CODE}"
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
                progress_callback("Copying custom files...")

            self._copy_custom_files_to_sectorfile()

            if progress_callback:
                progress_callback("Sectorfile installation complete!")

            return True

        except Exception as e:
            print(f"Error installing sectorfile: {e}")
            if progress_callback:
                progress_callback(f"Error: {e}")
            return False

    def _copy_custom_files_to_sectorfile(self) -> None:
        """Copy custom files from CustomFiles/{FIR_CODE} to Sectorfile/{FIR_CODE}."""
        try:
            custom_fir_path = self.path_manager.custom_fir_path(settings.FIR_CODE)

            if not custom_fir_path.exists():
                print(f"No custom files directory found at {custom_fir_path}")
                return

            sectorfile_fir_path = self.path_manager.sectorfile / settings.FIR_CODE

            if not sectorfile_fir_path.exists():
                print(f"Warning: Sectorfile FIR directory not found at {sectorfile_fir_path}")
                return

            # Subdirectories to copy
            subdirs = ["Alias", "ASR", "Plugins", "Settings", "Sounds"]

            for subdir in subdirs:
                source_dir = custom_fir_path / subdir
                dest_dir = sectorfile_fir_path / subdir

                if not source_dir.exists():
                    continue

                if not dest_dir.exists():
                    dest_dir.mkdir(parents=True, exist_ok=True)

                # Copy all files from source to destination
                for item in source_dir.iterdir():
                    dest_item = dest_dir / item.name

                    if item.is_file():
                        shutil.copy2(item, dest_item)
                        print(f"Copied custom file: {subdir}/{item.name}")
                    elif item.is_dir():
                        if dest_item.exists():
                            shutil.rmtree(dest_item)
                        shutil.copytree(item, dest_item)
                        print(f"Copied custom directory: {subdir}/{item.name}")

            print("Custom files copied successfully.")

        except Exception as e:
            print(f"Warning: Could not copy custom files: {e}")

    def _wait_for_zip_file(
        self, progress_callback: Optional[Callable[[str], None]] = None, timeout: int = None
    ) -> Optional[Path]:
        """Wait for a zip file to appear in the Sectorfile directory.

        Args:
            progress_callback: Optional callback for progress updates
            timeout: Maximum time to wait in seconds (default: from settings)

        Returns:
            Path to the zip file if found, None if timeout
        """
        if timeout is None:
            timeout = settings.SECTORFILE_DOWNLOAD_TIMEOUT

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
