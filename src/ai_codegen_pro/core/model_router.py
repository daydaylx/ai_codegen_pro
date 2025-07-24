import openai
import anthropic

class ModelRouter:
    """
    Zentrale Schnittstelle für KI-Modelle (OpenAI, OpenRouter, Anthropic etc.).
    """

    def __init__(self, provider="openai", api_key=None, api_base=None, model_name=None):
        self.provider = provider
        self.api_key = api_key
        self.api_base = api_base
        self.model_name = model_name

        if self.provider == "openai":
            openai.api_key = self.api_key
            if self.api_base:
                openai.api_base = self.api_base
        elif self.provider == "anthropic":
            anthropic.api_key = self.api_key

    def generate(self, prompt, **kwargs):
        """
        Führt eine Textgenerierung beim ausgewählten Provider aus.
        """
        if self.provider == "openai":
            response = openai.ChatCompletion.create(
                model=self.model_name or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model_name or "claude-3-haiku-20240307",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            raise NotImplementedError(f"Provider '{self.provider}' ist nicht implementiert.")
