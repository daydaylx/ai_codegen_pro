"""Professional Light Theme"""

from typing import Dict, Any
from PySide6.QtGui import QPalette, QColor
from .base_theme import BaseTheme


class LightTheme(BaseTheme):
    """Professional light theme"""

    @property
    def name(self) -> str:
        return "Professional Light"

    @property
    def colors(self) -> Dict[str, str]:
        return {
            "background": "#ffffff",
            "surface": "#f5f5f5",
            "surface_elevated": "#e9e9e9",
            "surface_hover": "#dddddd",
            "surface_active": "#cfcfcf",
            "text_primary": "#202020",
            "text_secondary": "#606060",
            "text_disabled": "#9d9d9d",
            "text_accent": "#0066cc",
            "border": "#c0c0c0",
            "border_focus": "#0066cc",
            "primary": "#0066cc",
            "primary_hover": "#0054a3",
        }

    @property
    def fonts(self) -> Dict[str, Dict[str, Any]]:
        return {}

    def get_stylesheet(self) -> str:
        # Reuse dark theme structure with light colors
        from .dark_theme import DarkTheme

        sheet = DarkTheme().get_stylesheet()

        # Replace dark colors with light colors
        dark_colors = DarkTheme().colors
        for dark_key, dark_value in dark_colors.items():
            if dark_key in self.colors:
                sheet = sheet.replace(dark_value, self.colors[dark_key])

        return sheet

    def get_palette(self) -> QPalette:
        palette = QPalette()
        c = self.colors

        palette.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(c["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(c["surface"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(c["text_primary"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(c["primary"]))

        return palette
