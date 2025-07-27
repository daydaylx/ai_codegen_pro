"""Settings Service für persistente Konfiguration"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .logger_service import LoggerService


class SettingsService:
    """Service für persistente Anwendungseinstellungen"""

    def __init__(self, config_file: Optional[Path] = None):
        self.logger = LoggerService().get_logger(__name__)

        if config_file:
            self.config_file = Path(config_file)
        else:
            config_dir = Path.home() / ".ai_codegen_pro"
            self.config_file = config_dir / "config.json"

        # Konfigurationsverzeichnis erstellen
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self._settings = {}
        self._load_settings()

    def _load_settings(self):
        """Lädt Settings aus der Konfigurationsdatei"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._settings = json.load(f)
                self.logger.debug(f"Settings geladen: {len(self._settings)} Einträge")
            else:
                self._settings = {}

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Settings: {e}")
            self._settings = {}

    def _save_settings(self):
        """Speichert Settings in die Konfigurationsdatei"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Gibt einen Konfigurationswert zurück"""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Setzt einen Konfigurationswert"""
        self._settings[key] = value
        self._save_settings()

    def get_all(self) -> Dict[str, Any]:
        """Gibt alle Konfigurationswerte zurück"""
        return self._settings.copy()

    def reset(self):
        """Setzt alle Konfigurationswerte zurück"""
        self._settings.clear()
        self._save_settings()
