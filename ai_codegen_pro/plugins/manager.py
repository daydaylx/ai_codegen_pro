"""Plugin Manager für AI CodeGen Pro"""

from typing import Dict
from pathlib import Path
import importlib
import inspect

from .base import BasePlugin
from ..utils.logger_service import LoggerService


class PluginManager:
    """Manager für Plugin-System"""

    def __init__(self):
        self.logger = LoggerService().get_logger(__name__)
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_registry = {}

    def load_plugin(self, plugin_path: Path) -> bool:
        """Plugin laden und registrieren"""
        try:
            module_name = plugin_path.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Plugin-Klassen finden
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BasePlugin)
                    and obj != BasePlugin
                ):

                    plugin_instance = obj()
                    if plugin_instance.initialize():
                        self.plugins[module_name] = plugin_instance
                        self.logger.info("Plugin loaded successfully")
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Plugin load failed: {e}")
            return False

    def get_plugin(self, name: str) -> BasePlugin:
        """Plugin abrufen"""
        return self.plugins.get(name)

    def list_plugins(self) -> Dict[str, BasePlugin]:
        """Alle Plugins auflisten"""
        return self.plugins.copy()

    def unload_plugin(self, name: str) -> bool:
        """Plugin entladen"""
        if name in self.plugins:
            del self.plugins[name]
            self.logger.info(f"Plugin {name} unloaded")
            return True
        return False
