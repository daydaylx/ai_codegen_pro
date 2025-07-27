"""
Unit tests for OpenRouter client.
"""

from unittest.mock import Mock, patch

import pytest
from ai_codecgen_pro.core.openrouter_client import OpenRouterClient, OpenRouterError


class TestOpenRouterClient:
    @pytest.fixture
    def client(self):
        return OpenRouterClient("test-api-key")

    @patch("ai_codegen_pro.core.openrouter_client.requests.Session.post")
    def test_generate_code_success(self, mock_post, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "def hello():\n    print('Hello, World!')"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = client.generate_code("Generate a hello world function")
        assert "def hello():" in result
        assert "Hello, World!" in result
        mock_post.assert_called_once()

    @patch("ai_codegen_pro.core.openrouter_client.requests.Session.post")
    def test_generate_code_api_error(self, mock_post, client):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        with pytest.raises(OpenRouterError):
            client.generate_code("test prompt")

    def test_check_connection_success(self, client):
        with patch.object(client, "get_available_models", return_value=[]):
            assert client.check_connection()

    def test_check_connection_failure(self, client):
        with patch.object(client, "get_available_models", side_effect=Exception()):
            assert not client.check_connection()
