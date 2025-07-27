"""Base-Klassen für Plugins"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from ..utils.logger_service import LoggerService


@dataclass
class PluginMetadata:
    """Metadata für ein Plugin"""

    name: str
    version: str
    description: str
    author: str
    homepage: str = ""
    dependencies: List[str] = field(default_factory=list)
    min_app_version: str = "0.1.0"


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
        """
        Initialisiert das Plugin

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Räumt Plugin-Ressourcen auf"""
        pass

    def is_enabled(self) -> bool:
        """Prüft ob Plugin aktiviert ist"""
        return self._enabled

    def is_initialized(self) -> bool:
        """Prüft ob Plugin initialisiert ist"""
        return self._initialized

    def enable(self) -> bool:
        """Aktiviert das Plugin"""
        if not self._initialized:
            if not self.initialize():
                return False

        self._enabled = True
        self.logger.info(f"Plugin {self.metadata.name} aktiviert")
        return True

    def disable(self) -> None:
        """Deaktiviert das Plugin"""
        self._enabled = False
        self.cleanup()
        self.logger.info(f"Plugin {self.metadata.name} deaktiviert")


class TemplatePlugin(PluginBase):
    """Basis-Klasse für Template-Plugins"""

    @abstractmethod
    def get_templates(self) -> Dict[str, str]:
        """
        Gibt verfügbare Templates zurück

        Returns:
            Dict mit {template_name: template_content}
        """
        pass

    @abstractmethod
    def get_template_categories(self) -> List[str]:
        """
        Gibt Template-Kategorien zurück

        Returns:
            Liste der Kategorien
        """
        pass

    def get_template_variables(self, template_name: str) -> Dict[str, Any]:
        """
        Gibt verfügbare Variablen für ein Template zurück

        Args:
            template_name: Name des Templates

        Returns:
            Dict mit Variablen-Definitionen
        """
        return {}

    def validate_template(self, template_name: str, variables: Dict[str, Any]) -> bool:
        """
        Validiert Template-Variablen

        Args:
            template_name: Name des Templates
            variables: Template-Variablen

        Returns:
            True wenn gültig, False sonst
        """
        return True


class ModelPlugin(PluginBase):
    """Basis-Klasse für Model-Provider-Plugins"""

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Gibt verfügbare Modelle zurück

        Returns:
            Liste der Model-Namen
        """
        pass

    @abstractmethod
    def generate_code(self, model: str, prompt: str, **kwargs) -> str:
        """
        Generiert Code mit dem angegebenen Modell

        Args:
            model: Model-Name
            prompt: Prompt
            **kwargs: Zusätzliche Parameter

        Returns:
            Generierter Code
        """
        pass

    def supports_streaming(self) -> bool:
        """Prüft ob Streaming unterstützt wird"""
        return False

    def generate_code_stream(self, model: str, prompt: str, **kwargs):
        """
        Generiert Code als Stream (falls unterstützt)

        Args:
            model: Model-Name
            prompt: Prompt
            **kwargs: Zusätzliche Parameter

        Yields:
            Code-Chunks
        """
        if not self.supports_streaming():
            raise NotImplementedError("Streaming wird nicht unterstützt")
