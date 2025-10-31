"""Application update dialog components."""

import flet as ft

from services import AppUpdateManager
from ui.components import BaseDialog


class MandatoryUpdateDialog(BaseDialog):
    """Dialog shown on Windows when application update is required.

    This dialog blocks the application from starting until the user
    initiates the update process.
    """

    def __init__(
            self,
            page: ft.Page,
            release_info: dict,
            update_manager: AppUpdateManager
    ):
        """Initialize mandatory update dialog.

        Args:
            page: Flet page instance
            release_info: Dictionary containing release information
                         (version, download_url, etc.)
            update_manager: AppUpdateManager instance for handling updates
        """
        self.release_info = release_info
        self.update_manager = update_manager
        self.progress_text = ft.Text("", size=12, italic=True)

        version = release_info.get("version", "unknown")

        content_column = ft.Column([
            ft.Text(
                f"A new version ({version}) is available and must be installed "
                "before you can use the application.\n\n"
                "Click 'Update Now' to download and install the update. "
                "The application will restart automatically.",
                size=14,
            ),
            ft.Container(height=10),
            self.progress_text,
        ])

        super().__init__(
            page=page,
            title="Update Required",
            content=content_column,
            actions=[
                ft.FilledButton(
                    text="Update Now",
                    on_click=lambda _: self._start_update(),
                )
            ],
            modal=True,
        )

    def _update_progress(self, message: str) -> None:
        """Update the progress text in the dialog.

        Args:
            message: Progress message to display
        """
        self.progress_text.value = message
        self.page.update()

    def _start_update(self) -> None:
        """Start the update process.

        Downloads the update, extracts it, and launches the updater script.
        """
        try:
            self.dialog.actions[0].disabled = True
            self.page.update()

            self._update_progress("Downloading update...")
            download_url = self.release_info["download_url"]
            zip_path = self.update_manager.download_update(download_url)

            self._update_progress("Extracting update...")
            new_version_path = self.update_manager.extract_update(zip_path)

            self._update_progress("Preparing to install update...")
            self.update_manager.launch_updater_and_exit(new_version_path, self.page)

        except Exception as e:
            self._update_progress("")
            error_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Update Failed"),
                content=ft.Text(
                    f"Failed to download or install the update:\n\n{str(e)}\n\n"
                    "Please try again or download the update manually from GitHub."
                ),
                actions=[
                    ft.TextButton(
                        text="Exit Application",
                        on_click=lambda _: self.page.window.close(),
                    ),
                ],
            )
            self.page.overlay.append(error_dialog)
            error_dialog.open = True
            self.page.update()

    def _retry_update(self, error_dialog: ft.AlertDialog) -> None:
        """Retry the update after a failure.

        Args:
            error_dialog: The error dialog to close
        """
        error_dialog.open = False
        if error_dialog in self.page.overlay:
            self.page.overlay.remove(error_dialog)

        self.dialog.actions[0].disabled = False
        self.page.update()


class UpdateAvailableDialog(BaseDialog):
    """Dialog shown on non-Windows platforms when update is available.

    This dialog is informational only and allows the user to continue
    using the application without updating.
    """

    def __init__(self, page: ft.Page, release_info: dict):
        """Initialize update available dialog.

        Args:
            page: Flet page instance
            release_info: Dictionary containing release information
                         (version, release_url, etc.)
        """
        self.release_info = release_info
        version = release_info.get("version", "unknown")
        release_url = release_info.get("release_url", "https://github.com/Lithuania-vACC/Sectorfile_Installer/releases")

        super().__init__(
            page=page,
            title="Update Available",
            content=(
                f"A new version ({version}) is available.\n\n"
                f"Please update when convenient by downloading from:\n"
                f"{release_url}"
            ),
            actions=[
                ft.TextButton(
                    text="OK",
                    on_click=lambda _: self.close(),
                )
            ],
            modal=False,
        )
