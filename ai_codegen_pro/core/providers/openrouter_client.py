"""OpenRouter API Client Implementation"""

import json
import requests
from typing import Dict, Any, Optional, List
from ...utils.logger_service import LoggerService


class OpenRouterError(Exception):
    """Custom exception for OpenRouter API errors"""

    pass


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger = LoggerService().get_logger(__name__)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ai-codegen-pro",
                "X-Title": "AI CodeGen Pro",
            }
        )

    def generate_code(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> str:
        """Generate code using specified model"""
        messages = self._prepare_messages(prompt, system_prompt)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            if stream:
                return self._handle_streaming_response(payload)
            else:
                return self._handle_single_response(payload)

        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            raise OpenRouterError(f"Failed to generate code: {e}")

    def _prepare_messages(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> List[Dict]:
        """Prepare messages for API request"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return messages

    def _handle_single_response(self, payload: Dict[str, Any]) -> str:
        """Handle non-streaming response"""
        response = self.session.post(
            f"{self.base_url}/chat/completions", json=payload, timeout=60
        )

        if response.status_code != 200:
            error_msg = f"API returned {response.status_code}: {response.text}"
            raise OpenRouterError(error_msg)

        result = response.json()

        if "choices" not in result or not result["choices"]:
            raise OpenRouterError("No response choices received")

        return result["choices"][0]["message"]["content"]

    def _handle_streaming_response(self, payload: Dict[str, Any]) -> str:
        """Handle streaming response"""
        payload["stream"] = True

        response = self.session.post(
            f"{self.base_url}/chat/completions", json=payload, stream=True, timeout=120
        )

        if response.status_code != 200:
            error_msg = (
                f"Streaming API returned {response.status_code}: " f"{response.text}"
            )
            raise OpenRouterError(error_msg)

        content = ""
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "choices" in data and data["choices"]:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            content += delta["content"]
                except json.JSONDecodeError:
                    continue

        return content

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/models")

            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                self.logger.warning(f"Failed to fetch models: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Error fetching models: {e}")
            return []

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about specific model"""
        models = self.list_models()

        for model in models:
            if model.get("id") == model_id:
                return model

        return None

    def validate_api_key(self) -> bool:
        """Validate API key by making test request"""
        try:
            models = self.list_models()
            return len(models) > 0
        except Exception:
            return False
