"""Plugin-Registry für die Verwaltung von Plugins"""

from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import importlib
import importlib.util
import inspect

from .base import PluginBase, TemplatePlugin, ModelPlugin, PluginMetadata
from ..utils.logger_service import LoggerService


class PluginRegistry:
    """Registry für Plugin-Verwaltung"""

    def __init__(self):
        self.logger = LoggerService().get_logger(__name__)
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._plugin_paths: List[Path] = []

        # Standard-Plugin-Verzeichnisse
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

        # System-Plugins
        try:
            import site

            for site_dir in site.getsitepackages():
                site_plugins = Path(site_dir) / "ai_codegen_pro_plugins"
                if site_plugins.exists():
                    self._plugin_paths.append(site_plugins)
        except Exception:
            pass

    def add_plugin_path(self, path: Path) -> None:
        """
        Fügt einen Plugin-Pfad hinzu

        Args:
            path: Pfad zum Plugin-Verzeichnis
        """
        if path.exists() and path not in self._plugin_paths:
            self._plugin_paths.append(path)
            self.logger.debug(f"Plugin-Pfad hinzugefügt: {path}")

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
            # Python-Files in diesem Verzeichnis
            for py_file in path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                self._load_plugin_from_file(py_file)

            # Plugin-Packages (Verzeichnisse mit __init__.py)
            for plugin_dir in path.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / "__init__.py").exists():
                    self._load_plugin_from_package(plugin_dir)

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

    def _load_plugin_from_package(self, package_path: Path) -> None:
        """Lädt Plugin aus einem Package"""
        try:
            module_name = f"plugin_{package_path.name}"
            spec = importlib.util.spec_from_file_location(
                module_name, package_path / "__init__.py"
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                self._extract_plugin_classes_from_module(module, str(package_path))

        except Exception as e:
            self.logger.warning(
                f"Konnte Plugin-Package nicht laden {package_path}: {e}"
            )

    def _extract_plugin_classes_from_module(
        self, module: Any, source_path: str
    ) -> None:
        """Extrahiert Plugin-Klassen aus einem Modul"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, PluginBase)
                and obj != PluginBase
                and obj != TemplatePlugin
                and obj != ModelPlugin
            ):

                plugin_id = f"{module.__name__}.{name}"
                self._plugin_classes[plugin_id] = obj

                self.logger.debug(
                    f"Plugin-Klasse gefunden: {plugin_id} in {source_path}"
                )

    def register_plugin_class(
        self, plugin_id: str, plugin_class: Type[PluginBase]
    ) -> None:
        """
        Registriert eine Plugin-Klasse manuell

        Args:
            plugin_id: Eindeutige Plugin-ID
            plugin_class: Plugin-Klasse
        """
        if not issubclass(plugin_class, PluginBase):
            raise ValueError("Plugin-Klasse muss von PluginBase erben")

        self._plugin_classes[plugin_id] = plugin_class
        self.logger.debug(f"Plugin-Klasse registriert: {plugin_id}")

    def create_plugin_instance(self, plugin_id: str) -> Optional[PluginBase]:
        """
        Erstellt eine Plugin-Instanz

        Args:
            plugin_id: Plugin-ID

        Returns:
            Plugin-Instanz oder None bei Fehler
        """
        if plugin_id not in self._plugin_classes:
            self.logger.error(f"Plugin-Klasse nicht gefunden: {plugin_id}")
            return None

        try:
            plugin_class = self._plugin_classes[plugin_id]
            instance = plugin_class()

            self.logger.debug(f"Plugin-Instanz erstellt: {plugin_id}")
            return instance

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen von Plugin {plugin_id}: {e}")
            return None

    def get_available_plugins(self) -> Dict[str, PluginMetadata]:
        """
        Gibt verfügbare Plugins zurück

        Returns:
            Dict mit {plugin_id: metadata}
        """
        plugins = {}

        for plugin_id, plugin_class in self._plugin_classes.items():
            try:
                # Temporäre Instanz für Metadata
                temp_instance = plugin_class()
                plugins[plugin_id] = temp_instance.metadata
            except Exception as e:
                self.logger.warning(f"Konnte Metadata für {plugin_id} nicht laden: {e}")

        return plugins

    def get_plugins_by_type(self, plugin_type: Type[PluginBase]) -> List[str]:
        """
        Gibt Plugin-IDs nach Typ zurück

        Args:
            plugin_type: Plugin-Typ (TemplatePlugin, ModelPlugin, etc.)

        Returns:
            Liste der Plugin-IDs
        """
        matching_plugins = []

        for plugin_id, plugin_class in self._plugin_classes.items():
            if issubclass(plugin_class, plugin_type):
                matching_plugins.append(plugin_id)

        return matching_plugins

    def validate_plugin_dependencies(self, plugin_id: str) -> bool:
        """
        Validiert Plugin-Dependencies

        Args:
            plugin_id: Plugin-ID

        Returns:
            True wenn alle Dependencies erfüllt sind
        """
        if plugin_id not in self._plugin_classes:
            return False

        try:
            temp_instance = self._plugin_classes[plugin_id]()
            dependencies = temp_instance.metadata.dependencies

            for dep in dependencies:
                try:
                    importlib.import_module(dep)
                except ImportError:
                    self.logger.error(f"Dependency fehlt für {plugin_id}: {dep}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Fehler bei Dependency-Prüfung für {plugin_id}: {e}")
            return False
