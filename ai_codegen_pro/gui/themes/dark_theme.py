"""Professional Dark Theme - VS Code inspired"""

from typing import Dict, Any
from PySide6.QtGui import QPalette, QColor
from .base_theme import BaseTheme


class DarkTheme(BaseTheme):
    """Professional dark theme inspired by VS Code Dark"""

    @property
    def name(self) -> str:
        return "Professional Dark"

    @property
    def colors(self) -> Dict[str, str]:
        return {
            # Main Colors
            "background": "#1e1e1e",
            "surface": "#252526",
            "surface_elevated": "#2d2d30",
            "surface_hover": "#3e3e42",
            "surface_active": "#094771",
            # Text Colors
            "text_primary": "#cccccc",
            "text_secondary": "#969696",
            "text_disabled": "#656565",
            "text_accent": "#007acc",
            # Border Colors
            "border": "#3c3c3c",
            "border_focus": "#007acc",
            "border_error": "#f14c4c",
            "border_success": "#89d185",
            # Status Colors
            "primary": "#007acc",
            "primary_hover": "#1177bb",
            "success": "#89d185",
            "warning": "#ffcc02",
            "error": "#f14c4c",
            "info": "#75beff",
        }

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
        }

    def get_stylesheet(self) -> str:
        c = self.colors
        return f"""
        QMainWindow {{
            background-color: {c['background']};
            color: {c['text_primary']};
        }}

        QWidget {{
            background-color: {c['background']};
            color: {c['text_primary']};
            font-family: Segoe UI;
            font-size: 9pt;
        }}

        QGroupBox {{
            font-weight: bold;
            font-size: 10pt;
            border: 2px solid {c['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 8px;
            background-color: {c['surface']};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: {c['text_accent']};
            background-color: {c['surface']};
        }}

        QPushButton {{
            background-color: {c['surface_elevated']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            color: {c['text_primary']};
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {c['surface_hover']};
            border-color: {c['border_focus']};
        }}

        QPushButton[class="primary"] {{
            background-color: {c['primary']};
            border-color: {c['primary']};
            color: white;
            font-weight: 600;
        }}

        QPushButton[class="primary"]:hover {{
            background-color: {c['primary_hover']};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 8px;
            color: {c['text_primary']};
            selection-background-color: {c['surface_active']};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c['border_focus']};
        }}

        QComboBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 6px 12px;
            color: {c['text_primary']};
        }}

        QTabWidget::pane {{
            border: 1px solid {c['border']};
            border-radius: 6px;
            background-color: {c['surface']};
        }}

        QTabBar::tab {{
            background-color: {c['surface_elevated']};
            border: 1px solid {c['border']};
            border-bottom: none;
            padding: 10px 20px;
            margin-right: 2px;
            color: {c['text_secondary']};
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}

        QTabBar::tab:selected {{
            background-color: {c['surface']};
            color: {c['text_primary']};
            border-bottom: 2px solid {c['primary']};
        }}
        """

    def get_palette(self) -> QPalette:
        palette = QPalette()
        c = self.colors

        palette.setColor(QPalette.ColorRole.Window, QColor(c["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(c["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(c["surface"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(c["text_primary"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(c["surface_active"]))

        return palette
