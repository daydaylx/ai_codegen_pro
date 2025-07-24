from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient

class ModelRouter:
    def __init__(self, provider, api_key, api_base=None, model_name=None):
        # provider ist nur noch für GUI-Kompatibilität, könnte entfallen
        self.model_name = model_name or "mistral-7b"
        self.api_key = api_key
        self.api_base = api_base

    def generate(self, prompt, systemprompt=None, **kwargs):
        client = OpenRouterClient(
            api_key=self.api_key,
            api_base=self.api_base,
            model=self.model_name
        )
        return client.generate(prompt, systemprompt=systemprompt, **kwargs)
