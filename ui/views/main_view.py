"""Main application view."""

import flet as ft
from pathlib import Path

from config.settings import settings
from services import (
    ConfigManager,
    Installer,
    Launcher,
    PathManager,
    ProfileManager,
    SectorVersionManager,
)
from ui.components import (
    InstallProgressDialog,
    NoProfilesDialog,
    SectorfileInstructionsDialog,
    SectorfileUpdateDialog,
    SettingsDialog,
    SettingsRequiredDialog,
)


class MainView(ft.View):
    """Main application view with logo and action buttons."""

    def __init__(self, page: ft.Page):
        """Initialize main view.

        Args:
            page: Flet page instance
        """
        super().__init__()
        self.page = page

        self.path_manager = PathManager()
        self.config_manager = ConfigManager(self.path_manager)
        self.installer = Installer(self.path_manager)
        self.launcher = Launcher()
        self.profile_manager = ProfileManager()

        self.route = "/"
        self.controls = [self._build_ui()]
        self.padding = 20
        self.spacing = 20

    def _build_ui(self) -> ft.Container:
        """Build the main UI.

        Returns:
            Container with all UI elements
        """
        self.logo = ft.Image(
            src=self._get_logo_path(),
            width=400,
            height=190,
            fit=ft.ImageFit.CONTAIN,
        )

        button_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="Settings",
                    icon="settings",
                    on_click=self._on_settings_click,
                    style=ft.ButtonStyle(
                        padding=ft.padding.all(20),
                    ),
                ),
                ft.ElevatedButton(
                    text="Fresh Install",
                    icon="download",
                    on_click=self._on_fresh_install_click,
                    style=ft.ButtonStyle(
                        padding=ft.padding.all(20),
                    ),
                ),
                ft.FilledButton(
                    text="Start",
                    icon="play_arrow",
                    on_click=self._on_start_click,
                    style=ft.ButtonStyle(
                        padding=ft.padding.all(20),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        )

        self.theme_button = ft.IconButton(
            icon=self._get_theme_icon(),
            on_click=self._on_theme_toggle,
            tooltip="Toggle theme",
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            self.theme_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self.logo,
                                button_row,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        expand=True,
                        alignment=ft.alignment.center,
                    ),
                ],
                spacing=0,
            ),
            expand=True,
        )

    def _on_settings_click(self, e: ft.ControlEvent) -> None:
        """Handle settings button click."""
        try:
            settings_dialog = SettingsDialog(self.page, self.config_manager)
            settings_dialog.show()
        except Exception as ex:
            print(f"Error opening settings: {ex}")
            import traceback
            traceback.print_exc()

    def _on_fresh_install_click(self, e: ft.ControlEvent) -> None:
        """Handle fresh install button click."""
        install_dialog = InstallProgressDialog(self.page, self.installer)
        install_dialog.show(on_complete_callback=self._show_sectorfile_install_dialog)

    def _show_sectorfile_install_dialog(self) -> None:
        """Show dialog with sectorfile installation instructions."""
        sectorfile_dialog = SectorfileInstructionsDialog(self.page, self.installer)
        sectorfile_dialog.show()

    def _on_start_click(self, e: ft.ControlEvent) -> None:
        """Handle start button click."""
        config = self.config_manager.config
        if not config.is_valid():
            settings_dialog = SettingsRequiredDialog(self.page)
            settings_dialog.show()
            return

        try:
            if SectorVersionManager.is_update_available():
                update_dialog = SectorfileUpdateDialog(self.page, self.installer)
                update_dialog.show()
                return
        except Exception as ex:
            print(f"Version check failed: {ex}")

        profiles = self.profile_manager.get_available_profiles(
            self.path_manager.sectorfile
        )

        if not profiles:
            no_profiles_dialog = NoProfilesDialog(self.page)
            no_profiles_dialog.show()
            return

        self._launch_and_exit(profiles[0])

    def _launch_and_exit(self, profile_name: str) -> None:
        """Launch EuroScope and AFV, then close the app.

        Args:
            profile_name: Name of the profile to launch (without .prf extension)
        """
        try:
            config = self.config_manager.config

            self.launcher.prepare_profiles(
                config=config,
                sectorfile_path=self.path_manager.sectorfile,
            )

            success = self.launcher.launch_euroscope(
                euroscope_path=self.path_manager.euroscope,
                profile_name=profile_name,
                sectorfile_path=self.path_manager.sectorfile,
            )

            if not success:
                print("Failed to launch EuroScope")
                return

            if config.afv_path:
                self.launcher.launch_afv(config.afv_path)

            import sys
            sys.exit(0)

        except Exception as ex:
            print(f"Error launching: {ex}")
            import traceback
            traceback.print_exc()

    def _get_logo_path(self) -> str:
        """Get the appropriate logo based on theme mode."""
        config = self.config_manager.config
        if config.theme_mode == "dark":
            logo_path = self.path_manager.assets / "vacc_lithuania_white_transparent.png"
        else:
            logo_path = self.path_manager.assets / "vacc_lithuania_darkgreen_transparent.png"

        return str(logo_path) if logo_path.exists() else None

    def _get_theme_icon(self) -> str:
        """Get the appropriate icon for current theme."""
        config = self.config_manager.config
        if config.theme_mode == "dark":
            return "dark_mode"
        else:
            return "light_mode"

    def _on_theme_toggle(self, e: ft.ControlEvent) -> None:
        """Toggle between light and dark theme."""
        config = self.config_manager.config

        if config.theme_mode == "light":
            config.theme_mode = "dark"
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            config.theme_mode = "light"
            self.page.theme_mode = ft.ThemeMode.LIGHT

        self.config_manager.save(config)

        self.theme_button.icon = self._get_theme_icon()
        self.logo.src = self._get_logo_path()
        self.page.update()
