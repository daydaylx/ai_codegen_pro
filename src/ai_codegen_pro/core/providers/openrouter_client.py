import requests
import json
import time

class OpenRouterClient:
    def __init__(self, api_key, api_base=None, model=None):
        self.api_key = api_key
        self.api_base = api_base or "https://openrouter.ai/api/v1"
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "ai_codegen_pro"
        }

    def get_available_models(self):
        url = f"{self.api_base}/models"
        r = requests.get(url, headers=self.headers, timeout=10)
        r.raise_for_status()
        return r.json().get("data", [])

    def generate(self, prompt, systemprompt=None, max_tokens=2048, temperature=0.7):
        url = f"{self.api_base}/chat/completions"
        
        messages = []
        if systemprompt:
            messages.append({"role": "system", "content": systemprompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        r = requests.post(url, headers=self.headers, json=data, timeout=40)
        r.raise_for_status()
        result = r.json()
        return result["choices"][0]["message"]["content"]

    def generate_code_streaming(self, prompt, systemprompt=None, max_tokens=2048, temperature=0.7, chunk_size=40):
        url = f"{self.api_base}/chat/completions"
        
        messages = []
        if systemprompt:
            messages.append({"role": "system", "content": systemprompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        with requests.post(url, headers=self.headers, json=data, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            buffer = ""
            for line in resp.iter_lines():
                if not line or not line.startswith(b"data: "):
                    continue
                payload = line.removeprefix(b"data: ").decode("utf-8")
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        buffer += delta
                        if len(buffer) >= chunk_size:
                            yield buffer
                            buffer = ""
                except (json.JSONDecodeError, KeyError):
                    continue
            if buffer:
                yield buffer
