"""Professional Light Theme – basiert auf BaseTheme."""

from typing import Dict, Any
from PySide6.QtGui import QPalette, QColor
from .base_theme import BaseTheme


class LightTheme(BaseTheme):
    name = "Professional Light"

    # -------------------------------------------------------------
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
            "success": "#3498db",  # Example for light theme success
            "warning": "#f39c12",  # Example for light theme warning
            "error": "#e74c3c",  # Example for light theme error
            "info": "#9b59b6",  # Example for light theme info
            "syntax_keyword": "#0000ff",  # Blue for keywords
            "syntax_string": "#800000",  # Maroon for strings
            "syntax_comment": "#008000",  # Green for comments
            "syntax_number": "#800080",  # Purple for numbers
            "syntax_function": "#000080",  # Dark Blue for functions
            "syntax_class": "#800080",  # Purple for classes
        }

    # -------------------------------------------------------------
    @property
    def fonts(self) -> Dict[str, Dict[str, Any]]:
        return {
            "main": {"family": "Segoe UI", "size": 9, "weight": "normal"},
            "code": {
                "family": 'Consolas, "Courier New", monospace',
                "size": 10,
                "weight": "normal",
            },
            "heading": {"family": "Segoe UI", "size": 12, "weight": "bold"},
            "small": {"family": "Segoe UI", "size": 8, "weight": "normal"},
        }

    # -------------------------------------------------------------
    def get_stylesheet(self) -> str:
        # Für Kürze reuse des Dark-Styles, nur Farben anders
        from .dark_theme import DarkTheme

        sheet = DarkTheme().get_stylesheet()
        for k, v in DarkTheme().colors.items():
            sheet = sheet.replace(v, self.colors.get(k, v))
        return sheet

    # -------------------------------------------------------------
    def get_palette(self) -> QPalette:
        pal = QPalette()
        c = self.colors
        pal.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(c["text_primary"]))
        pal.setColor(QPalette.ColorRole.Base, QColor(c["surface"]))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(c["surface_elevated"]))
        pal.setColor(QPalette.ColorRole.Text, QColor(c["text_primary"]))
        pal.setColor(
            QPalette.ColorRole.BrightText, QColor("#000000")
        )  # Black for bright text on light
        pal.setColor(QPalette.ColorRole.Button, QColor(c["surface_elevated"]))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(c["text_primary"]))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(c["primary"]))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        return pal
