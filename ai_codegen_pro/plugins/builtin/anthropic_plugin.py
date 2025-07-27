"""Anthropic Claude Model Plugin"""

from typing import List
import requests
from ..base import ModelPlugin, PluginMetadata


class AnthropicModelPlugin(ModelPlugin):
    """Plugin für Anthropic Claude Modelle"""

    def __init__(self):
        super().__init__()
        self.api_key = None
        self.base_url = "https://api.anthropic.com/v1"

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Anthropic Claude",
            version="1.0.0",
            description="Anthropic Claude AI Modelle",
            author="AI CodeGen Pro",
            dependencies=["requests"],
        )

    def initialize(self) -> bool:
        # API Key aus Settings laden
        from ...utils.settings_service import SettingsService

        settings = SettingsService()
        self.api_key = settings.get("anthropic_api_key")

        if not self.api_key:
            self.logger.warning("Anthropic API Key nicht gefunden")
            return False

        self._initialized = True
        self.logger.info("Anthropic Plugin initialisiert")
        return True

    def cleanup(self) -> None:
        self.api_key = None
        self.logger.info("Anthropic Plugin bereinigt")

    def get_available_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
        ]

    def generate_code(self, model: str, prompt: str, **kwargs) -> str:
        """Generiert Code mit Anthropic Claude"""
        if not self.api_key:
            raise Exception("Anthropic API Key nicht konfiguriert")

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": model,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "messages": [{"role": "user", "content": prompt}],
        }

        # System prompt falls vorhanden
        if "system_prompt" in kwargs:
            data["system"] = kwargs["system_prompt"]

        # Weitere Parameter
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]

        response = requests.post(
            f"{self.base_url}/messages", headers=headers, json=data, timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Anthropic API Fehler: {response.text}")

        result = response.json()
        return result["content"][0]["text"]

    def supports_streaming(self) -> bool:
        return True

    def generate_code_stream(self, model: str, prompt: str, **kwargs):
        """Generiert Code als Stream"""
        if not self.api_key:
            raise Exception("Anthropic API Key nicht konfiguriert")

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": model,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }

        if "system_prompt" in kwargs:
            data["system"] = kwargs["system_prompt"]

        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]

        with requests.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=data,
            stream=True,
            timeout=120,
        ) as response:

            if response.status_code != 200:
                raise Exception(f"Anthropic API Fehler: {response.text}")

            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    try:
                        import json

                        data = json.loads(line[6:])

                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {})
                            if "text" in delta:
                                yield delta["text"]
                    except Exception:
                        continue
