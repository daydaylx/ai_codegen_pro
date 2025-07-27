"""Plugin-Manager für die zentrale Plugin-Verwaltung"""

from typing import Dict, Any

from .base import PluginBase, TemplatePlugin
from .registry import PluginRegistry
from ..utils.logger_service import LoggerService
from ..utils.settings_service import SettingsService


class PluginManager:
    """Zentraler Plugin-Manager"""

    def __init__(self):
        self.logger = LoggerService().get_logger(__name__)
        self.settings = SettingsService()
        self.registry = PluginRegistry()

        self._active_plugins: Dict[str, PluginBase] = {}
        self._plugin_config: Dict[str, Dict[str, Any]] = {}

        self._initialize()

    def _initialize(self):
        """Initialisiert das Plugin-System"""
        self.logger.info("Plugin-System wird initialisiert...")

        self.registry.discover_plugins()
        self._load_plugin_config()
        self._load_auto_enabled_plugins()

        plugin_count = len(self._active_plugins)
        self.logger.info(
            f"Plugin-System initialisiert mit {plugin_count} aktiven Plugins"
        )

    def _load_plugin_config(self):
        """Lädt Plugin-Konfiguration"""
        try:
            self._plugin_config = self.settings.get("plugins", {})
        except Exception as e:
            self.logger.warning(f"Konnte Plugin-Konfiguration nicht laden: {e}")
            self._plugin_config = {}

    def _save_plugin_config(self):
        """Speichert Plugin-Konfiguration"""
        try:
            self.settings.set("plugins", self._plugin_config)
        except Exception as e:
            self.logger.error(f"Konnte Plugin-Konfiguration nicht speichern: {e}")

    def _load_auto_enabled_plugins(self):
        """Lädt automatisch aktivierte Plugins"""
        for plugin_id, config in self._plugin_config.items():
            if config.get("auto_enable", False):
                self.enable_plugin(plugin_id)

    def enable_plugin(self, plugin_id: str, auto_enable: bool = False) -> bool:
        """Aktiviert ein Plugin"""
        if plugin_id in self._active_plugins:
            return True

        plugin = self.registry.create_plugin_instance(plugin_id)
        if not plugin:
            return False

        if plugin.enable():
            self._active_plugins[plugin_id] = plugin

            if plugin_id not in self._plugin_config:
                self._plugin_config[plugin_id] = {}

            self._plugin_config[plugin_id]["auto_enable"] = auto_enable
            self._save_plugin_config()

            self.logger.info(f"Plugin aktiviert: {plugin_id}")
            return True

        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Deaktiviert ein Plugin"""
        if plugin_id not in self._active_plugins:
            return False

        plugin = self._active_plugins[plugin_id]
        plugin.disable()

        del self._active_plugins[plugin_id]

        if plugin_id in self._plugin_config:
            self._plugin_config[plugin_id]["auto_enable"] = False
            self._save_plugin_config()

        self.logger.info(f"Plugin deaktiviert: {plugin_id}")
        return True

    def get_active_plugins(self) -> Dict[str, PluginBase]:
        """Gibt aktive Plugins zurück"""
        return self._active_plugins.copy()

    def get_template_plugins(self) -> Dict[str, TemplatePlugin]:
        """Gibt aktive Template-Plugins zurück"""
        result = {}
        for plugin_id, plugin in self._active_plugins.items():
            if isinstance(plugin, TemplatePlugin):
                result[plugin_id] = plugin
        return result

    def get_all_templates(self) -> Dict[str, str]:
        """Sammelt alle Templates von aktiven Template-Plugins"""
        all_templates = {}

        for plugin_id, plugin in self.get_template_plugins().items():
            try:
                plugin_templates = plugin.get_templates()

                for template_name, template_content in plugin_templates.items():
                    prefixed_name = f"{plugin.metadata.name}/{template_name}"
                    all_templates[prefixed_name] = template_content

            except Exception as e:
                self.logger.error(
                    f"Fehler beim Laden von Templates aus {plugin_id}: {e}"
                )

        return all_templates

    def get_available_plugins(self) -> Dict[str, Any]:
        """Gibt verfügbare Plugins mit Status zurück"""
        available = self.registry.get_available_plugins()
        result = {}

        for plugin_id, metadata in available.items():
            result[plugin_id] = {
                "metadata": metadata,
                "enabled": plugin_id in self._active_plugins,
                "dependencies_ok": True,
                "config": self._plugin_config.get(plugin_id, {}),
            }

        return result

    def reload_plugins(self):
        """Lädt alle Plugins neu"""
        self.logger.info("Plugin-System wird neu geladen...")

        for plugin_id in list(self._active_plugins.keys()):
            self.disable_plugin(plugin_id)

        self.registry = PluginRegistry()
        self.registry.discover_plugins()

        self._load_auto_enabled_plugins()

        self.logger.info("Plugin-System neu geladen")

    def shutdown(self):
        """Räumt Plugin-System auf"""
        self.logger.info("Plugin-System wird heruntergefahren...")

        for plugin_id in list(self._active_plugins.keys()):
            self.disable_plugin(plugin_id)

        self._active_plugins.clear()
        self.logger.info("Plugin-System heruntergefahren")
