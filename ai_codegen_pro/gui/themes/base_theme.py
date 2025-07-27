"""Base Theme Class"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from PySide6.QtGui import QPalette


class BaseTheme(ABC):
    """Base class for all themes"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Theme name"""
        pass

    @property
    @abstractmethod
    def colors(self) -> Dict[str, str]:
        """Theme color palette"""
        pass

    @property
    @abstractmethod
    def fonts(self) -> Dict[str, Dict[str, Any]]:
        """Theme fonts"""
        pass

    @abstractmethod
    def get_stylesheet(self) -> str:
        """Get complete stylesheet"""
        pass

    @abstractmethod
    def get_palette(self) -> QPalette:
        """Get Qt palette"""
        pass
