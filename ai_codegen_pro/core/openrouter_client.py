"""
OpenRouter API Client with proper error handling and retry logic.
"""
import logging
from typing import Dict, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """Custom exception for OpenRouter API errors."""

    pass


class OpenRouterClient:
    """Production-ready OpenRouter API client."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _make_request(self, endpoint: str, payload: Dict[str, object]) -> Dict[str, object]:
        """Make authenticated request with error handling."""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "AI CodeGen Pro",
        }

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise OpenRouterError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise OpenRouterError("Connection error")
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}"
            try:
                error_data = e.response.json()
                msg = error_data.get("error", {}).get("message", "Unknown error")
                error_msg += f": {msg}"
            except Exception:
                pass
            raise OpenRouterError(error_msg)
        except Exception as exc:
            raise OpenRouterError(f"Unexpected error: {str(exc)}")

    def generate_code(
        self,
        prompt: str,
        model: str = "anthropic/claude-3-sonnet-20240229",
        max_tokens: int = 4000,
        temperature: float = 0.1,
    ) -> str:
        """Generate code using specified model."""
        system_content = (
            "You are an expert programmer. Generate clean, "
            "well-documented, production-ready code."
        )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_content,
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        logger.info(f"Generating code with model: {model}")
        response = self._make_request("chat/completions", payload)

        try:
            generated_code = response["choices"][0]["message"]["content"]
            logger.info(f"Generated {len(generated_code)} characters of code")
            return generated_code
        except (KeyError, IndexError) as e:
            raise OpenRouterError(f"Invalid response format: {e}")

    def get_available_models(self) -> List[Dict[str, object]]:
        """Get list of available models."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as exc:
            logger.error(f"Failed to fetch models: {exc}")
            return []

    def check_connection(self) -> bool:
        """Test API connectivity."""
        try:
            self.get_available_models()
            return True
        except Exception:
            return False
