"""
Base classes and registry for the plugin system.
"""

from typing import Dict, Type


class CodeGenPlugin:
    def on_load(self, app):
        pass

    def on_unload(self):
        pass

    def on_post_generate(self, file, result):
        pass


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, CodeGenPlugin] = {}

    def register(self, name: str, plugin_cls: Type[CodeGenPlugin], app):
        plugin = plugin_cls()
        plugin.on_load(app)
        self._plugins[name] = plugin

    def unregister(self, name: str):
        if name in self._plugins:
            self._plugins[name].on_unload()
            del self._plugins[name]

    def run_post_generate(self, file, result):
        for plugin in self._plugins.values():
            plugin.on_post_generate(file, result)
