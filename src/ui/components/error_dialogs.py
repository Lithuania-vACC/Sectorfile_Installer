"""Error dialog components."""

from typing import Callable, Optional

import flet as ft
from services import Installer
from ui.components import BaseDialog


class SectorfileUpdateDialog(BaseDialog):
    """Dialog shown when sectorfile needs to be updated."""

    def __init__(self, page: ft.Page, installer: Installer, on_complete: Optional[Callable] = None):
        """Initialize sectorfile update dialog.

        Args:
            page: Flet page instance
            installer: Installer service instance
            on_complete: Optional callback to run after update completes
        """
        self.installer = installer
        self.on_complete = on_complete

        super().__init__(
            page=page,
            title="Sectorfile Update Required",
            content=(
                "A new sectorfile version is available and must be installed.\n\n"
                "Click OK to begin the update process. Your browser will open "
                "to download the new sectorfile."
            ),
            actions=[
                ft.FilledButton(
                    text="OK",
                    on_click=lambda _: self._on_ok_click(),
                )
            ]
        )

    def _on_ok_click(self) -> None:
        """Handle OK button click - start sectorfile update process."""
        from ui.components import SectorfileInstructionsDialog

        self.close()

        install_dialog = SectorfileInstructionsDialog(self.page, self.installer)
        install_dialog.show()

        if self.on_complete:
            self.on_complete()


class SettingsRequiredDialog(BaseDialog):
    """Dialog shown when required settings are not configured."""

    def __init__(self, page: ft.Page):
        """Initialize settings required dialog.

        Args:
            page: Flet page instance
        """
        super().__init__(
            page=page,
            title="Settings Required",
            content=(
                "Please fill in all required settings before starting:\n"
                "- VATSIM User ID\n"
                "- VATSIM Password\n"
                "- VATSIM Rating\n\n"
                "Click the Settings button to configure these.\n\n"
            )
        )


class NoProfilesDialog(BaseDialog):
    """Dialog shown when no EuroScope profiles are found."""

    def __init__(self, page: ft.Page):
        """Initialize no profiles dialog.

        Args:
            page: Flet page instance
        """
        super().__init__(
            page=page,
            title="No Profiles Found",
            content=(
                "No EuroScope profiles (.prf files) found in the Sectorfile directory. "
                "Please run a fresh install first."
            )
        )
