"""Settings dialog component."""

import flet as ft
from pathlib import Path

from models import UserConfig, VatsimRating
from services import ConfigManager


class SettingsDialog:
    """Settings configuration dialog."""

    def __init__(self, page: ft.Page, config_manager: ConfigManager):
        """Initialize settings dialog.

        Args:
            page: Flet page instance
            config_manager: Config manager service
        """
        self.page = page
        self.config_manager = config_manager

        # Form fields
        self.name_field = ft.TextField(
            label="Name",
            value=self.config_manager.config.name,
            autofocus=True,
            width=260
        )

        self.vatsim_id_field = ft.TextField(
            label="VATSIM ID",
            value=self.config_manager.config.vatsim_id,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=260,
        )

        self.vatsim_password_field = ft.TextField(
            label="VATSIM Password",
            value=self.config_manager.config.vatsim_password,
            password=True,
            can_reveal_password=True,
            width=260,
        )

        self.rating_dropdown = ft.Dropdown(
            label="Rating",
            value=self.config_manager.config.rating.value if self.config_manager.config.rating else None,
            options=[ft.dropdown.Option(rating.value) for rating in VatsimRating],
            width=260,
            dense=True,
        )

        self.hoppie_code_field = ft.TextField(
            label="Hoppie Code",
            value=self.config_manager.config.hoppie_code,
            password=True,
            can_reveal_password=True,
            width=260
        )

        self.browse_button = ft.IconButton(
            icon="folder_open",
            icon_size=18,
            on_click=self._on_browse_click,
            tooltip="Browse...",
            padding=ft.padding.all(3),
        )

        self.afv_path_field = ft.TextField(
            label="Audio for VATSIM Path",
            value=self.config_manager.config.afv_path,
            read_only=True,
            suffix=self.browse_button,
            width=260,
            height=48,
            dense=True
        )

        left_column = ft.Column(
            controls=[
                self.name_field,
                self.vatsim_id_field,
                self.vatsim_password_field,
            ],
            spacing=5,
            expand=True,
        )

        right_column = ft.Column(
            controls=[
                self.rating_dropdown,
                self.hoppie_code_field,
                self.afv_path_field,
            ],
            spacing=5,
            expand=True,
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Settings"),
            content=ft.Container(
                content=ft.Row(
                    controls=[left_column, right_column],
                    spacing=15,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                width=550,
            ),
            actions=[
                ft.TextButton(
                    text="Cancel",
                    on_click=self._on_cancel_click,
                ),
                ft.FilledButton(
                    text="Save",
                    on_click=self._on_save_click,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def show(self) -> None:
        """Show the settings dialog."""
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def _on_browse_click(self, e: ft.ControlEvent) -> None:
        """Handle browse button click."""
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.page.overlay.append(self.file_picker)
        self.page.update()
        self.file_picker.pick_files(
            dialog_title="Audio for VATSIM Path",
            allowed_extensions=["exe"],
            file_type=ft.FilePickerFileType.CUSTOM,
        )

    def _on_file_picked(self, e: ft.FilePickerResultEvent) -> None:
        """Handle file picker result."""
        if e.files:
            self.afv_path_field.value = e.files[0].path
        if hasattr(self, 'file_picker') and self.file_picker in self.page.overlay:
            self.page.overlay.remove(self.file_picker)
        self.page.update()

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Handle cancel button click."""
        self.dialog.open = False
        self.page.update()
        if self.dialog in self.page.overlay:
            self.page.overlay.remove(self.dialog)

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Handle save button click."""
        # Validate required fields
        if not (
            self.name_field.value
            and self.vatsim_id_field.value
            and self.vatsim_password_field.value
            and self.rating_dropdown.value
        ):
            self._show_error(
                "Missing Data",
                "Please fill in all required fields: Name, VATSIM ID, Password, and Rating.",
            )
            return

        config = UserConfig(
            name=self.name_field.value,
            vatsim_id=self.vatsim_id_field.value,
            vatsim_password=self.vatsim_password_field.value,
            rating=VatsimRating(self.rating_dropdown.value),
            hoppie_code=self.hoppie_code_field.value,
            afv_path=self.afv_path_field.value,
            theme_mode=self.config_manager.config.theme_mode,
            euroscope_version=self.config_manager.config.euroscope_version,
            sectorfile_airac=self.config_manager.config.sectorfile_airac,
        )

        self.config_manager.save(config)

        self.dialog.open = False
        self.page.update()
        if self.dialog in self.page.overlay:
            self.page.overlay.remove(self.dialog)

    def _show_error(self, title: str, message: str) -> None:
        """Show an error dialog.

        Args:
            title: Error title
            message: Error message
        """
        self.error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Text(message, size=14),
                padding=10,
            ),
            actions=[
                ft.FilledButton(text="OK", on_click=self._close_error_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.error_dialog)
        self.error_dialog.open = True
        self.page.update()

    def _close_error_dialog(self) -> None:
        """Close the error dialog."""
        if hasattr(self, 'error_dialog'):
            self.error_dialog.open = False
            if self.error_dialog in self.page.overlay:
                self.page.overlay.remove(self.error_dialog)
            self.page.update()
