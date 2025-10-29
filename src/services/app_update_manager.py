import os
import sys
import json
import zipfile
import subprocess
from pathlib import Path
from typing import Optional
from packaging import version as pkg_version

import requests

from config.settings import settings
from services.path_manager import PathManager


class AppUpdateManager:
    """Manages application version checking and auto-updates."""

    @staticmethod
    def get_current_version() -> str:
        """Get the current application version from settings.

        Returns:
            Version string in format MAJOR.MINOR.PATCH (e.g., "2.1.1")
        """
        return settings.APP_VERSION

    @staticmethod
    def get_latest_release() -> Optional[dict]:
        """Fetch the latest release information from GitHub.

        Queries the GitHub API to get the latest release, including version
        and download URL for the main.dist.zip asset.

        Returns:
            Dictionary with keys:
                - version (str): Version string (e.g., "2.1.0")
                - tag_name (str): Git tag (e.g., "v2.1.0")
                - download_url (str): Direct download URL for main.dist.zip
                - release_url (str): GitHub release page URL
            Returns None if API call fails or release not found

        Raises:
            None - Returns None on any error to allow graceful degradation
        """
        url = (
            f"{settings.GITHUB_API_BASE}/repos/"
            f"{settings.GITHUB_REPO_OWNER}/"
            f"{settings.GITHUB_REPO_NAME}/releases/latest"
        )

        try:
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print(f"GitHub API returned status {response.status_code}")
                return None

            data = response.json()

            tag_name = data.get("tag_name", "")
            version_str = tag_name.lstrip("v")

            assets = data.get("assets", [])
            download_url = None

            for asset in assets:
                if asset.get("name") == settings.UPDATE_ASSET_NAME:
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                print(f"Asset '{settings.UPDATE_ASSET_NAME}' not found in release")
                return None

            return {
                "version": version_str,
                "tag_name": tag_name,
                "download_url": download_url,
                "release_url": data.get("html_url", ""),
            }

        except requests.exceptions.RequestException as e:
            print(f"Network error while checking for updates: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error while checking for updates: {e}")
            return None

    @staticmethod
    def is_update_available() -> tuple[bool, Optional[dict]]:
        """Check if a newer application version is available.

        Compares the current version with the latest GitHub release version
        using semantic versioning comparison.

        Returns:
            Tuple of (is_available, release_info):
                - is_available (bool): True if update is available
                - release_info (dict|None): Release information dict or None
        """
        try:
            current_version = AppUpdateManager.get_current_version()
            latest_release = AppUpdateManager.get_latest_release()

            if not latest_release:
                return False, None

            latest_version = latest_release["version"]

            current_ver = pkg_version.parse(current_version)
            latest_ver = pkg_version.parse(latest_version)

            if latest_ver > current_ver:
                return True, latest_release
            else:
                return False, None

        except Exception as e:
            print(f"Error checking for application update: {e}")
            return False, None

    @staticmethod
    def download_update(download_url: str, progress_callback=None) -> str:
        """Download the update zip file from GitHub.

        Args:
            download_url: Direct download URL for main.dist.zip
            progress_callback: Optional callback function for progress updates
                               (currently not implemented)

        Returns:
            Path to downloaded zip file

        Raises:
            Exception: If download fails
        """
        # Create temp directory if it doesn't exist
        os.makedirs(settings.UPDATE_TEMP_DIR, exist_ok=True)

        zip_path = os.path.join(settings.UPDATE_TEMP_DIR, "main.dist.zip")

        try:
            print(f"Downloading update from {download_url}...")
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        # TODO: Call progress_callback if provided

            print(f"Download complete: {zip_path}")
            return zip_path

        except Exception as e:
            raise Exception(f"Failed to download update: {e}")

    @staticmethod
    def extract_update(zip_path: str) -> str:
        """Extract the downloaded update zip file.

        Args:
            zip_path: Path to the downloaded zip file

        Returns:
            Path to the extracted main.dist directory

        Raises:
            Exception: If extraction fails
        """
        extract_dir = os.path.join(settings.UPDATE_TEMP_DIR, "new_version")

        try:
            if os.path.exists(extract_dir):
                import shutil
                shutil.rmtree(extract_dir)

            os.makedirs(extract_dir, exist_ok=True)

            print(f"Extracting update to {extract_dir}...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            extracted_items = os.listdir(extract_dir)

            main_dist_path = os.path.join(extract_dir, "main.dist")
            if os.path.exists(main_dist_path) and os.path.isdir(main_dist_path):
                print(f"Extraction complete: {main_dist_path}")
                return main_dist_path
            else:
                print(f"Extraction complete: {extract_dir}")
                return extract_dir

        except Exception as e:
            raise Exception(f"Failed to extract update: {e}")

    @staticmethod
    def get_installation_directory() -> str:
        """Get the current application installation directory.

        Returns:
            Path to the directory containing the running executable
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return str(Path(sys.executable).parent)
        else:
            return str(Path(__file__).parent.parent / "assets")

    @staticmethod
    def launch_updater_and_exit(new_version_path: str, page=None):
        """Launch the updater script and exit the application.

        This function will start the updater batch script, which will:
        1. Wait for this process to exit
        2. Replace old files with new files
        3. Restart the application
        4. Clean up temporary files

        Args:
            new_version_path: Path to the extracted new version files
            page: Optional Flet page instance for proper window closing

        Note:
            This function exits the application via page.window.destroy() if page
            is provided, otherwise uses sys.exit(0)
        """
        install_dir = PathManager().root
        exe_path = install_dir / "main.exe"
        updater_script = ".\\updater.bat"

        if not os.path.exists(updater_script):
            raise FileNotFoundError(
                f"Updater script not found at {updater_script}. "
                "The application may not have been built correctly."
            )

        # Create updater config file
        config_path = install_dir / "updater_config.json"
        config_data = {
            "new_version_path": str(new_version_path),
            "install_path": str(install_dir),
            "exe_path": str(exe_path)
        }

        print(f"Creating updater config at: {config_path}")
        print(f"New version path: {new_version_path}")
        print(f"Installation directory: {install_dir}")
        print(f"Executable path: {exe_path}")

        try:
            with open(config_path, "w") as config_file:
                json.dump(config_data, config_file, indent=2)
        except Exception as e:
            raise Exception(f"Failed to create updater config file: {e}")

        with open("update_log.txt", "a") as log_file:
            log_file.write(f"Launching updater with config:\n")
            log_file.write(f"Config path: {config_path}\n")
            log_file.write(f"New version path: {new_version_path}\n")
            log_file.write(f"Installation directory: {install_dir}\n")
            log_file.write(f"Executable path: {exe_path}\n\n")

        try:
            # Launch batch script with cmd.exe to ensure it runs properly
            subprocess.Popen(
                f'cmd.exe /c start "" /min "{updater_script}"',
                cwd=install_dir,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except Exception as e:
            raise Exception(f"Failed to launch updater: {e}")

        print("Exiting application for update...")

        if page:
            # Properly close the Flet window
            page.window.destroy()
        else:
            sys.exit(0)
