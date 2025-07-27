"""Theme Manager for global theme application"""

from typing import Dict, Type

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from .base_theme import BaseTheme
from .dark_theme import DarkTheme
from .light_theme import LightTheme


class ThemeManager(QObject):
    """Manages application themes"""

    theme_changed = Signal()

    def __init__(self):
        super().__init__()
        self._themes: Dict[str, Type[BaseTheme]] = {
            "dark": DarkTheme,
            "light": LightTheme,
        }
        self._current_theme_name = "dark"
        self._current_theme = DarkTheme()

    def set_theme(self, theme_name: str):
        """Set active theme"""
        if theme_name not in self._themes:
            raise ValueError(f"Unknown theme: {theme_name}")

        theme_class = self._themes[theme_name]
        self._current_theme = theme_class()
        self._current_theme_name = theme_name

        self.apply_theme()
        self.theme_changed.emit()

    def toggle_theme(self):
        """Toggle between light and dark"""
        new_theme = "light" if self._current_theme_name == "dark" else "dark"
        self.set_theme(new_theme)

    def get_current_theme(self) -> BaseTheme:
        """Get current theme instance"""
        return self._current_theme

    def get_current_theme_name(self) -> str:
        """Get current theme name"""
        return self._current_theme_name

    def apply_theme(self):
        """Apply current theme to application"""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(self._current_theme.get_stylesheet())
            app.setPalette(self._current_theme.get_palette())
