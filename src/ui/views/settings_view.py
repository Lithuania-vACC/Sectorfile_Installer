"""Full-window settings view."""

import flet as ft

from config import settings
from models import UserConfig, VatsimRating
from services import ConfigManager
from ui.components import BaseDialog


class SettingsView(ft.View):
    """Full-window settings configuration view."""

    def __init__(self, page: ft.Page, config_manager: ConfigManager):
        super().__init__()
        self.page = page
        self.config_manager = config_manager
        self.route = "/settings"
        self.padding = 0
        self._build_fields()
        self.controls = [self._build_ui()]

    def _build_fields(self) -> None:
        config = self.config_manager.config

        self.name_field = ft.TextField(
            label="Name",
            value=config.name,
            autofocus=True,
            expand=True,
            dense=True,
        )

        self.rating_dropdown = ft.DropdownM2(
            label="Rating",
            value=config.rating.value if config.rating else None,
            options=[ft.dropdown.Option(r.value) for r in VatsimRating],
            expand=True,
            dense=True,
            border=ft.InputBorder.OUTLINE,
            border_radius=4,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
        )

        self.vatsim_id_field = ft.TextField(
            label="VATSIM ID",
            value=config.vatsim_id,
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
            dense=True,
        )

        self.hoppie_code_field = ft.TextField(
            label="Hoppie Code",
            value=config.hoppie_code,
            password=True,
            can_reveal_password=True,
            expand=True,
            dense=True,
        )

        self.vatsim_password_field = ft.TextField(
            label="VATSIM Password",
            value=config.vatsim_password,
            password=True,
            can_reveal_password=True,
            expand=True,
            dense=True,
        )

        self.afv_path_field = ft.TextField(
            label="Audio for VATSIM",
            value=config.afv_path,
            read_only=True,
            expand=True,
            dense=True,
            height=40,
            suffix=ft.IconButton(
                icon="folder_open",
                icon_size=18,
                on_click=self._on_browse_afv_click,
                tooltip="Browse...",
                padding=ft.padding.all(3),
            ),
        )

        self.vatis_path_field = ft.TextField(
            label="vATIS",
            value=config.vatis_path,
            read_only=True,
            expand=True,
            dense=True,
            height=40,
            suffix=ft.IconButton(
                icon="folder_open",
                icon_size=18,
                on_click=self._on_browse_vatis_click,
                tooltip="Browse...",
                padding=ft.padding.all(3),
            ),
        )

    def _build_ui(self) -> ft.Column:
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon="arrow_back",
                        on_click=self._go_back,
                        tooltip="Back",
                        icon_size=18,
                        style=ft.ButtonStyle(padding=ft.padding.all(6)),
                    ),
                    ft.Text("Settings", size=15, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    ft.Text(
                        f"v{settings.APP_VERSION}",
                        size=11,
                        color="#9E9E9E",
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=6, right=14, top=0, bottom=0),
            height=36,
        )

        section_divider = ft.Row(
            controls=[
                ft.Text("File Paths", size=11, color="#9E9E9E"),
                ft.Container(
                    expand=True,
                    height=1,
                    bgcolor="#9E9E9E",
                    opacity=0.4,
                    margin=ft.margin.only(left=8, top=3),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        content = ft.ListView(
            controls=[
                ft.Row(
                    [self.name_field, self.rating_dropdown],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=5),
                ft.Row(
                    [self.vatsim_id_field, self.hoppie_code_field],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=5),
                self.vatsim_password_field,
                ft.Container(height=3),
                section_divider,
                ft.Container(height=6),
                self.afv_path_field,
                ft.Container(height=5),
                self.vatis_path_field,
                ft.Container(height=9),
                ft.Row(
                    controls=[
                        ft.Container(expand=True),
                        ft.TextButton(text="Cancel", on_click=self._go_back),
                        ft.FilledButton(text="Save", on_click=self._on_save_click),
                    ],
                ),
            ],
            spacing=0,
            padding=ft.padding.only(left=24, right=24, top=10, bottom=4),
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        return ft.Column(
            controls=[
                header,
                ft.Divider(height=1, thickness=1),
                content,
            ],
            spacing=0,
            expand=True,
        )

    def _go_back(self, _: ft.ControlEvent = None) -> None:
        self.page.views.pop()
        self.page.update()

    def _on_browse_afv_click(self, _: ft.ControlEvent) -> None:
        self._afv_picker = ft.FilePicker(on_result=self._on_afv_picked)
        self.page.overlay.append(self._afv_picker)
        self.page.update()
        self._afv_picker.pick_files(
            dialog_title="Audio for VATSIM Path",
            allowed_extensions=["exe"],
            file_type=ft.FilePickerFileType.CUSTOM,
        )

    def _on_afv_picked(self, e: ft.FilePickerResultEvent) -> None:
        if e.files:
            self.afv_path_field.value = e.files[0].path
        if self._afv_picker in self.page.overlay:
            self.page.overlay.remove(self._afv_picker)
        self.page.update()

    def _on_browse_vatis_click(self, _: ft.ControlEvent) -> None:
        self._vatis_picker = ft.FilePicker(on_result=self._on_vatis_picked)
        self.page.overlay.append(self._vatis_picker)
        self.page.update()
        self._vatis_picker.pick_files(
            dialog_title="vATIS Path",
            allowed_extensions=["exe"],
            file_type=ft.FilePickerFileType.CUSTOM,
        )

    def _on_vatis_picked(self, e: ft.FilePickerResultEvent) -> None:
        if e.files:
            self.vatis_path_field.value = e.files[0].path
        if self._vatis_picker in self.page.overlay:
            self.page.overlay.remove(self._vatis_picker)
        self.page.update()

    def _on_save_click(self, _: ft.ControlEvent) -> None:
        if not (
            self.vatsim_id_field.value
            and self.vatsim_password_field.value
            and self.rating_dropdown.value
        ):
            self._show_error(
                "Missing Data",
                "Please fill in all required fields: VATSIM ID, Password, and Rating.",
            )
            return

        config = UserConfig(
            name=self.name_field.value,
            vatsim_id=self.vatsim_id_field.value,
            vatsim_password=self.vatsim_password_field.value,
            rating=VatsimRating(self.rating_dropdown.value),
            hoppie_code=self.hoppie_code_field.value,
            afv_path=self.afv_path_field.value,
            vatis_path=self.vatis_path_field.value,
            theme_mode=self.config_manager.config.theme_mode,
        )

        self.config_manager.save(config)
        self._go_back()

    def _show_error(self, title: str, message: str) -> None:
        error_dialog = BaseDialog(self.page, title, message)
        error_dialog.show()
