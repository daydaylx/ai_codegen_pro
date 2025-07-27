from typing import Dict, Type

from ai_codegen_pro.plugins.base import CodeGenPlugin, PluginRegistry


class PluginManager:
    def __init__(self, app_reference):
        self.registry = PluginRegistry()
        self.app = app_reference

    def load_plugin(self, name: str, plugin_cls: Type[CodeGenPlugin]):
        if name in self.registry._plugins:
            raise RuntimeError(f"Plugin {name} bereits geladen.")
        self.registry.register(name, plugin_cls, self.app)
        print(f"Plugin {name} geladen.")

    def unload_plugin(self, name: str):
        if name not in self.registry._plugins:
            raise RuntimeError(f"Plugin {name} nicht gefunden.")
        self.registry.unregister(name)
        print(f"Plugin {name} entladen.")

    def list_plugins(self) -> Dict[str, CodeGenPlugin]:
        return dict(self.registry._plugins)

    def trigger_post_generate(self, files, generation_result):
        self.registry.run_post_generate(files, generation_result)
