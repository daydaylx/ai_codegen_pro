"""OpenRouter API Client für KI-basierte Codegenerierung"""

import requests
from ..utils.logger_service import LoggerService


class OpenRouterClient:
    """Client für die OpenRouter API"""

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = LoggerService().get_logger(__name__)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def generate_code(
        self,
        model: str,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generiert Code mit dem angegebenen Modell
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions", json=data, timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            self.logger.error(f"OpenRouter API error: {e}")
            raise Exception(f"Code generation failed: {e}")

    def list_models(self) -> list:
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []
