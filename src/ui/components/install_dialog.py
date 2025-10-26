"""Installation dialog components."""

import flet as ft

from services import Installer


class InstallProgressDialog:
    """Dialog showing EuroScope installation progress."""

    def __init__(self, page: ft.Page, installer: Installer):
        """Initialize install progress dialog.

        Args:
            page: Flet page instance
            installer: Installer service
        """
        self.page = page
        self.installer = installer

        self.progress_text = ft.Text("Starting installation...", size=16)
        self.progress_bar = ft.ProgressBar(width=400)

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Installing EuroScope"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.progress_text,
                        self.progress_bar,
                    ],
                    tight=True,
                    spacing=20,
                ),
                width=500,
                padding=20,
            ),
        )

    def show(self, on_complete_callback=None):
        """Show the dialog and start installation.

        Args:
            on_complete_callback: Callback to run when installation completes
        """
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

        def progress_callback(message: str) -> None:
            """Update progress text."""
            self.progress_text.value = message
            self.page.update()

        try:
            success = self.installer.install_euroscope(
                version="3.2.10", progress_callback=progress_callback
            )

            if success:
                self.progress_text.value = "EuroScope installation complete!"
                self.progress_bar.visible = False
                self.page.update()

                self.close()

                if on_complete_callback:
                    on_complete_callback()
            else:
                self.progress_text.value = "Installation failed!"
                self.progress_bar.visible = False
                self.dialog.actions = [
                    ft.TextButton(text="Close", on_click=lambda _: self.close())
                ]
        except Exception as ex:
            self.progress_text.value = f"Error: {ex}"
            self.progress_bar.visible = False
            self.dialog.actions = [
                ft.TextButton(text="Close", on_click=lambda _: self.close())
            ]

        self.page.update()

    def close(self):
        """Close the dialog."""
        self.dialog.open = False
        self.page.update()
        if self.dialog in self.page.overlay:
            self.page.overlay.remove(self.dialog)


class SectorfileInstructionsDialog:
    """Dialog with instructions for manual sectorfile download."""

    def __init__(self, page: ft.Page, installer: Installer):
        """Initialize sectorfile instructions dialog.

        Args:
            page: Flet page instance
            installer: Installer service
        """
        self.page = page
        self.installer = installer

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Manual Sectorfile Download Required"),
            content=ft.Container(
                content=ft.Text(
                    "Due to changes in GNG, you must manually download the sectorfile.\n\n"
                    "When you press OK:\n"
                    "1. Your web browser will open the AeroNav GNG page\n"
                    "2. Log in with your Navigraph and VATSIM accounts\n"
                    "3. Download the ZIP file to the Sectorfile folder that will open\n"
                    "4. The installer will detect and extract it automatically",
                    size=14,
                ),
                width=500,
                height=300,
                padding=0,
            ),
            actions=[
                ft.FilledButton(
                    text="OK",
                    on_click=lambda _: self._on_ok_click(),
                )
            ],
        )

    def show(self):
        """Show the dialog."""
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close(self):
        """Close the dialog."""
        self.dialog.open = False
        self.page.update()
        if self.dialog in self.page.overlay:
            self.page.overlay.remove(self.dialog)

    def _on_ok_click(self):
        """Handle OK button click."""
        self.close()

        self._show_progress_dialog()

    def _show_progress_dialog(self):
        """Show progress dialog and start installation."""
        progress_text = ft.Text("Opening browser and file explorer...", size=16)
        progress_bar = ft.ProgressBar(width=400)

        progress_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Installing Sectorfile"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        progress_text,
                        progress_bar,
                    ],
                    tight=True,
                    spacing=20,
                ),
                width=500,
                padding=20,
            ),
        )

        self.page.overlay.append(progress_dialog)
        progress_dialog.open = True
        self.page.update()

        def progress_callback(message: str) -> None:
            """Update progress text."""
            progress_text.value = message
            self.page.update()

        try:
            success = self.installer.install_sectorfile(progress_callback=progress_callback)

            if success:
                progress_text.value = "Sectorfile installation complete!"
                progress_bar.visible = False
                progress_dialog.actions = [
                    ft.FilledButton(
                        text="OK",
                        on_click=lambda _: self._close_progress_dialog(progress_dialog),
                    )
                ]
            else:
                progress_text.value = "Installation failed or timed out"
                progress_bar.visible = False
                progress_dialog.actions = [
                    ft.TextButton(
                        text="Close",
                        on_click=lambda _: self._close_progress_dialog(progress_dialog),
                    )
                ]
        except Exception as ex:
            progress_text.value = f"Error: {ex}"
            progress_bar.visible = False
            progress_dialog.actions = [
                ft.TextButton(
                    text="Close",
                    on_click=lambda _: self._close_progress_dialog(progress_dialog),
                )
            ]

        self.page.update()

    def _close_progress_dialog(self, dialog: ft.AlertDialog):
        """Close the progress dialog."""
        dialog.open = False
        self.page.update()
        if dialog in self.page.overlay:
            self.page.overlay.remove(dialog)
