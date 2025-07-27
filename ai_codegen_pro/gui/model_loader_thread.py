import logging
import time

from PySide6.QtCore import QThread, Signal

log = logging.getLogger(__name__)


class ModelLoaderThread(QThread):
    models_loaded = Signal(list)

    def __init__(self, model_source=None):
        super().__init__()
        self.model_source = model_source

    def run(self):
        log.info("ModelLoaderThread gestartet")
        try:
            time.sleep(1)
            dummy_models = [
                {"name": "openai/gpt-4", "provider": "OpenAI"},
                {"name": "mistral-7b", "provider": "OpenRouter"},
                {"name": "deepseek-coder", "provider": "DeepSeek"},
            ]
            self.models_loaded.emit(dummy_models)
        except Exception as e:
            log.error(f"Fehler beim Laden der Modelle: {e}")
            self.models_loaded.emit([])
