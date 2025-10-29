import os
import sys
import zipfile
import subprocess
from pathlib import Path
from typing import Optional
from packaging import version as pkg_version

import requests

from config.settings import settings

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions


class AppUpdateManager:
    """Manages application version checking and auto-updates."""

    @staticmethod
    def get_current_version() -> str:
        """Get the current application version from pyproject.toml.

        Returns:
            Version string in format MAJOR.MINOR.PATCH (e.g., "2.0.0")

        Raises:
            FileNotFoundError: If pyproject.toml cannot be found
            ValueError: If version cannot be parsed from pyproject.toml
        """
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
            pyproject_path = app_dir.parent.parent / "pyproject.toml"
            if not pyproject_path.exists():
                raise FileNotFoundError(
                    "pyproject.toml not found. Version information unavailable."
                )
        else:
            current_file = Path(__file__)
            pyproject_path = current_file.parent.parent.parent / "pyproject.toml"

        if not pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                version = data.get("project", {}).get("version")

                if not version:
                    raise ValueError("Version field not found in pyproject.toml")

                return version
        except Exception as e:
            raise ValueError(f"Failed to parse version from pyproject.toml: {e}")

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
            return str(Path(__file__).parent.parent.parent / "main.dist")

    @staticmethod
    def launch_updater_and_exit(new_version_path: str):
        """Launch the updater script and exit the application.

        This function will start the updater batch script, which will:
        1. Wait for this process to exit
        2. Replace old files with new files
        3. Restart the application
        4. Clean up temporary files

        Args:
            new_version_path: Path to the extracted new version files

        Note:
            This function does not return - it exits the application
        """
        install_dir = AppUpdateManager.get_installation_directory()
        exe_path = sys.executable
        updater_script = os.path.join(install_dir, "updater.bat")

        if not os.path.exists(updater_script):
            raise FileNotFoundError(
                f"Updater script not found at {updater_script}. "
                "The application may not have been built correctly."
            )

        print(f"Launching updater script: {updater_script}")
        print(f"New version path: {new_version_path}")
        print(f"Installation directory: {install_dir}")
        print(f"Executable path: {exe_path}")

        try:
            subprocess.Popen(
                [updater_script, new_version_path, install_dir, exe_path],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                close_fds=True,
            )
        except Exception as e:
            raise Exception(f"Failed to launch updater: {e}")

        print("Exiting application for update...")
        sys.exit(0)
