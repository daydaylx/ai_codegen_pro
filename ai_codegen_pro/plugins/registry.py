"""Plugin-Registry für die Verwaltung von Plugins"""

from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import importlib
import importlib.util
import inspect

from .base import PluginBase, TemplatePlugin, PluginMetadata
from ..utils.logger_service import LoggerService


class PluginRegistry:
    """Registry für Plugin-Verwaltung"""

    def __init__(self):
        self.logger = LoggerService().get_logger(__name__)
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._plugin_paths: List[Path] = []

        self._setup_plugin_paths()

    def _setup_plugin_paths(self):
        """Richtet Standard-Plugin-Pfade ein"""
        # Interne Plugins
        internal_plugins = Path(__file__).parent / "builtin"
        self._plugin_paths.append(internal_plugins)

        # User-Plugins
        user_plugins = Path.home() / ".ai_codegen_pro" / "plugins"
        user_plugins.mkdir(parents=True, exist_ok=True)
        self._plugin_paths.append(user_plugins)

    def discover_plugins(self) -> None:
        """Entdeckt alle Plugins in den registrierten Pfaden"""
        self.logger.info("Suche nach Plugins...")

        for plugin_path in self._plugin_paths:
            if not plugin_path.exists():
                continue

            self._discover_plugins_in_path(plugin_path)

        self.logger.info(f"{len(self._plugin_classes)} Plugin-Klassen entdeckt")

    def _discover_plugins_in_path(self, path: Path) -> None:
        """Entdeckt Plugins in einem spezifischen Pfad"""
        try:
            for py_file in path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                self._load_plugin_from_file(py_file)

        except Exception as e:
            self.logger.error(f"Fehler beim Entdecken von Plugins in {path}: {e}")

    def _load_plugin_from_file(self, file_path: Path) -> None:
        """Lädt Plugin aus einer Python-Datei"""
        try:
            module_name = f"plugin_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                self._extract_plugin_classes_from_module(module, str(file_path))

        except Exception as e:
            self.logger.warning(f"Konnte Plugin nicht laden {file_path}: {e}")

    def _extract_plugin_classes_from_module(
        self, module: Any, source_path: str
    ) -> None:
        """Extrahiert Plugin-Klassen aus einem Modul"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, PluginBase)
                and obj != PluginBase
                and obj != TemplatePlugin
            ):

                plugin_id = f"{module.__name__}.{name}"
                self._plugin_classes[plugin_id] = obj

                self.logger.debug(f"Plugin-Klasse gefunden: {plugin_id}")

    def create_plugin_instance(self, plugin_id: str) -> Optional[PluginBase]:
        """Erstellt eine Plugin-Instanz"""
        if plugin_id not in self._plugin_classes:
            return None

        try:
            plugin_class = self._plugin_classes[plugin_id]
            instance = plugin_class()
            return instance

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen von Plugin {plugin_id}: {e}")
            return None

    def get_available_plugins(self) -> Dict[str, PluginMetadata]:
        """Gibt verfügbare Plugins zurück"""
        plugins = {}

        for plugin_id, plugin_class in self._plugin_classes.items():
            try:
                temp_instance = plugin_class()
                plugins[plugin_id] = temp_instance.metadata
            except Exception as e:
                self.logger.warning(f"Konnte Metadata für {plugin_id} nicht laden: {e}")

        return plugins
