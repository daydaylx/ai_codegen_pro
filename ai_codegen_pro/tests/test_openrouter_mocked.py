import pytest
from unittest.mock import patch
from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient
from requests.exceptions import RequestException


@patch("requests.post")
def test_generate_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "print('Hello, world!')"}}]
    }
    client = OpenRouterClient(api_key="test-key", model="dummy")
    result = client.generate("Sag hallo!")
    assert "print" in result


@patch("requests.post", side_effect=RequestException("API DOWN"))
def test_generate_api_error(mock_post):
    client = OpenRouterClient(api_key="bad", model="dummy")
    with pytest.raises(RuntimeError):
        client.generate("Test")
