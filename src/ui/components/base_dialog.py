"""Base dialog component."""

from typing import Optional

import flet as ft


class BaseDialog:
    """Base class for modal dialogs."""

    def __init__(
            self,
            page: ft.Page,
            title: str,
            content: str | ft.Control,
            actions: Optional[list[ft.Control]] = None,
            modal: bool = True
    ):
        """Initialize base dialog.

        Args:
            page: Flet page instance
            title: Dialog title
            content: Dialog content (string or Control)
            actions: List of action buttons
            modal: Whether dialog is modal
        """
        self.page = page

        content_control = ft.Text(content) if isinstance(content, str) else content

        self.dialog = ft.AlertDialog(
            modal=modal,
            title=ft.Text(title),
            content=content_control,
            actions=actions or [
                ft.TextButton(
                    text="OK",
                    on_click=lambda _: self.close(),
                )
            ],
        )

    def show(self) -> None:
        """Show the dialog."""
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close(self) -> None:
        """Close the dialog."""
        self.dialog.open = False
        self.page.update()
        if self.dialog in self.page.overlay:
            self.page.overlay.remove(self.dialog)
