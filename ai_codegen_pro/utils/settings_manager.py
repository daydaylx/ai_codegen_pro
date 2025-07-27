import json
from pathlib import Path


class SettingsManager:
    def __init__(self, path=None):
        self.config_path = Path(path or "~/.ai_codegen_pro.json").expanduser()
        self._cfg = self.load()

    def load(self):
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.config_path, "w") as f:
            json.dump(self._cfg, f, indent=2)

    def get(self, key, default=None):
        return self._cfg.get(key, default)

    def set(self, key, value):
        self._cfg[key] = value
        self.save()
