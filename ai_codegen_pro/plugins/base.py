"""Base-Klassen für Plugins"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..utils.logger_service import LoggerService


@dataclass
class PluginMetadata:
    """Metadata für ein Plugin"""

    name: str
    version: str
    description: str
    author: str
    homepage: str = ""
    dependencies: List[str] = None
    min_app_version: str = "0.1.0"

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class PluginBase(ABC):
    """Basis-Klasse für alle Plugins"""

    def __init__(self):
        self.logger = LoggerService().get_logger(self.__class__.__name__)
        self._metadata: Optional[PluginMetadata] = None
        self._enabled = False
        self._initialized = False

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Plugin-Metadaten"""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """Initialisiert das Plugin"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Räumt Plugin-Ressourcen auf"""
        pass

    def is_enabled(self) -> bool:
        return self._enabled

    def enable(self) -> bool:
        if not self._initialized:
            if not self.initialize():
                return False
        self._enabled = True
        return True

    def disable(self) -> None:
        self._enabled = False
        self.cleanup()


class TemplatePlugin(PluginBase):
    """Basis-Klasse für Template-Plugins"""

    @abstractmethod
    def get_templates(self) -> Dict[str, str]:
        """Gibt verfügbare Templates zurück"""
        pass

    @abstractmethod
    def get_template_categories(self) -> List[str]:
        """Gibt Template-Kategorien zurück"""
        pass
