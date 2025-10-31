"""Main application entry point."""

import platform
import flet as ft

from config import settings
from services import ConfigManager, PathManager, AppUpdateManager
from ui.components import MandatoryUpdateDialog, UpdateAvailableDialog
from ui.views import MainView


def is_app_update_available(page: ft.Page) -> bool:
    """Check for application updates on startup.

    On Windows: Shows a mandatory update dialog if update is available.
                User must update before using the application.

    On other platforms: Shows an informational dialog if update is available.
                       User can continue without updating.

    Args:
        page: Flet page instance

    Returns:
        bool: False if application should continue to main view, True otherwise
    """
    try:
        update_manager = AppUpdateManager()

        # Check if update is available
        is_available, release_info = update_manager.is_update_available()

        if not is_available:
            # No update needed, continue normally
            return False

        # Update is available
        is_windows = platform.system() == "Windows"

        if is_windows:
            # Show mandatory update dialog (blocks until update completes)
            dialog = MandatoryUpdateDialog(page, release_info, update_manager)
            dialog.show()
            # If user closes dialog or update fails, they can't proceed
            return True
        else:
            # Show informational dialog (non-blocking)
            dialog = UpdateAvailableDialog(page, release_info)
            dialog.show()
            # User can continue using the app after closing dialog
            return False

    except Exception as e:
        # If update check fails (e.g., no internet), just log and continue
        print(f"Update check failed: {e}")
        return False


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
    page.window.maximizable = False

    page.update()

    icon_path = path_manager.assets / "icon.ico"
    if icon_path.exists():
        page.window.icon = str(icon_path)

    page.update()

    update_available = is_app_update_available(page)

    if update_available:
        return

    main_view = MainView(page)

    page.views.clear()
    page.views.append(main_view)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
