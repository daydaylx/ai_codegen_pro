import json
from pathlib import Path

class SettingsManager:
    def __init__(self, filename=".ai_codegen_pro_config.json"):
        self.config_path = Path.home() / filename
        self.settings = self._load()

    def _load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self._save()

    def _save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
