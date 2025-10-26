"""Service for launching EuroScope and AFV."""

import subprocess
from pathlib import Path
from typing import Optional

import psutil

from config.settings import settings
from models import UserConfig


class Launcher:
    """Handles launching applications."""

    def prepare_profiles(self, config: UserConfig, sectorfile_path: Path) -> None:
        """Prepare profile files with user credentials before launching.

        This updates all .prf files in the sectorfile directory with the user's
        VATSIM credentials and writes the hoppie code to the appropriate file.

        Args:
            config: User configuration with credentials
            sectorfile_path: Path to sectorfile directory
        """
        try:
            hoppie_file = (
                sectorfile_path
                / settings.FIR_CODE
                / "Plugins"
                / "Topsky"
                / "TopSkyCPDLChoppieCode.txt"
            )
            if hoppie_file.parent.exists():
                hoppie_file.write_text(config.hoppie_code)

            rating_numeric = config.rating.numeric_value if config.rating else 0

            for prf_file in sectorfile_path.rglob("*.prf"):
                self._update_profile_credentials(
                    prf_file,
                    name=config.name,
                    vatsim_id=config.vatsim_id,
                    password=config.vatsim_password,
                    rating=rating_numeric,
                )

        except Exception as e:
            print(f"Error preparing profiles: {e}")

    def _update_profile_credentials(
        self,
        profile_path: Path,
        name: str,
        vatsim_id: str,
        password: str,
        rating: int,
    ) -> None:
        """Update a profile file with user credentials.

        Args:
            profile_path: Path to the .prf file
            name: User's name
            vatsim_id: User's VATSIM ID
            password: User's VATSIM password
            rating: Numeric rating value
        """
        try:
            lines = profile_path.read_text().splitlines()

            filtered_lines = [
                line
                for line in lines
                if not (
                    line.startswith("LastSession\trealname")
                    or line.startswith("LastSession\tcertificate")
                    or line.startswith("LastSession\tpassword")
                    or line.startswith("LastSession\trating")
                )
            ]

            filtered_lines.extend(
                [
                    f"LastSession\trealname\t{name}",
                    f"LastSession\tcertificate\t{vatsim_id}",
                    f"LastSession\tpassword\t{password}",
                    f"LastSession\trating\t{rating}",
                ]
            )

            profile_path.write_text("\n".join(filtered_lines))

        except Exception as e:
            print(f"Error updating profile {profile_path}: {e}")

    def launch_euroscope(
        self, euroscope_path: Path, profile_name: str, sectorfile_path: Path
    ) -> bool:
        """Launch EuroScope with a specific profile.

        Args:
            euroscope_path: Path to EuroScope directory
            profile_name: Name of the profile to load (without .prf)
            sectorfile_path: Path to sectorfile directory

        Returns:
            True if launched successfully, False otherwise
        """
        try:
            exe_path = euroscope_path / "EuroScope.exe"
            if not exe_path.exists():
                print(f"EuroScope.exe not found at {exe_path}")
                return False

            profile_path = f"..\\Sectorfile\\{profile_name}.prf"

            command = f'start "" "{exe_path}" "{profile_path}"'
            subprocess.Popen(
                command,
                shell=True,
                cwd=str(euroscope_path),
                start_new_session=True
            )

            return True

        except Exception as e:
            print(f"Error launching EuroScope: {e}")
            return False

    def launch_afv(self, afv_path: str) -> bool:
        """Launch Audio for VATSIM (AFV).

        Args:
            afv_path: Path to AFV executable

        Returns:
            True if launched successfully, False otherwise
        """
        if not afv_path or not Path(afv_path).exists():
            return False

        try:
            exe_name = Path(afv_path).name

            if self._is_process_running(exe_name):
                print(f"{exe_name} is already running")
                return True

            import platform
            if platform.system() == "Windows":
                import ctypes
                import services.path_manager

                shortcut_lnk = str(services.path_manager.PathManager().temp) + "/afv_launcher.lnk"
                if not Path(shortcut_lnk).exists():
                    import lnkcreator
                    lnkcreator.create_shortcut(
                        shortcut_path=shortcut_lnk,
                        target=afv_path,
                        arguments=[],
                        asadmin=True
                    )
                ctypes.windll.shell32.ShellExecuteW(None, "runas", shortcut_lnk, None, None, None)
            else:
                subprocess.Popen(
                    [afv_path],
                    shell=False,
                    start_new_session=True
                )
            return True

        except Exception as e:
            print(f"Error launching AFV: {e}")
            return False

    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is currently running.

        Args:
            process_name: Name of the process to check

        Returns:
            True if running, False otherwise
        """
        try:
            for process in psutil.process_iter(["name"]):
                if process.info["name"].lower() == process_name.lower():
                    return True
        except Exception as e:
            print(f"Error checking process: {e}")

        return False
