from ai_codegen_pro.utils.logger_service import log
from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient

class ModelRouter:
    """
    Zentrale Orchestrierung für Modellaufrufe (aktuell nur OpenRouter).
    """

    def __init__(self, api_key, api_base=None, model_name=None):
        self.model_name = model_name or "mistral-7b"
        self.api_key = api_key
        self.api_base = api_base
        try:
            self.client = OpenRouterClient(
                api_key=self.api_key,
                api_base=self.api_base,
                model=self.model_name
            )
        except Exception as e:
            log.error(f"ModelRouter-Initialisierung fehlgeschlagen: {e}")
            raise

    def generate(self, prompt, systemprompt=None, **kwargs):
        try:
            return self.client.generate(prompt, systemprompt=systemprompt, **kwargs)
        except Exception as e:
            log.error(f"Fehler bei der Generierung: {e}")
            raise

    def generate_streaming(self, prompt, systemprompt=None, **kwargs):
        try:
            return self.client.generate_code_streaming(prompt, systemprompt=systemprompt, **kwargs)
        except Exception as e:
            log.error(f"Fehler beim Streaming: {e}")
            raise
