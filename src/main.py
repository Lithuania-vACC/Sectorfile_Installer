"""Main application entry point."""

import base64
import flet as ft
from pathlib import Path

from assets.icon_b64 import IMAGE_B64 as ICON_B64
from config.settings import settings
from services import ConfigManager, PathManager
from ui.components.settings_dialog import SettingsDialog
from ui.views.main_view import MainView


def main(page: ft.Page) -> None:
    """Main application entry point.

    Args:
        page: Flet page instance
    """
    path_manager = PathManager()
    config_manager = ConfigManager(path_manager)

    path_manager.ensure_base_directories()
    path_manager.ensure_fir_directories(settings.FIR_CODE)

    config = config_manager.load()

    if config.theme_mode == "system":
        import darkdetect
        is_dark = darkdetect.isDark()
        config.theme_mode = "dark" if is_dark else "light"
        config_manager.save(config)

    page.title = settings.APP_NAME

    if config.theme_mode == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    page.window.width = settings.WINDOW_WIDTH
    page.window.height = settings.WINDOW_HEIGHT
    page.window.resizable = False

    icon_path = path_manager.assets / "icon.ico"
    if icon_path.exists():
        page.window.icon = str(icon_path)

    main_view = MainView(page)

    page.views.clear()
    page.views.append(main_view)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
