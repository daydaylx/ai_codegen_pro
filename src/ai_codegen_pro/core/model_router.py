import openai
import anthropic
import time

class ModelRouter:
    """
    Zentrale Schnittstelle für KI-Modelle (OpenAI, OpenRouter, Anthropic etc.)
    mit Fallback-Option für mehrere Modelle/Provider.
    """

    def __init__(self, providers=None, api_keys=None, api_bases=None, model_names=None):
        # Neue Argumente erlauben jetzt Listen für Fallback-Ketten!
        self.providers = providers if isinstance(providers, list) else [providers or "openai"]
        self.api_keys = api_keys if isinstance(api_keys, list) else [api_keys]
        self.api_bases = api_bases if isinstance(api_bases, list) else [api_bases]
        self.model_names = model_names if isinstance(model_names, list) else [model_names]
    
    def generate(self, prompt, **kwargs):
        """
        Führt eine Textgenerierung beim ersten verfügbaren Provider aus.
        """
        last_error = None
        for idx, provider in enumerate(self.providers):
            api_key = self.api_keys[min(idx, len(self.api_keys)-1)]
            api_base = self.api_bases[min(idx, len(self.api_bases)-1)]
            model_name = self.model_names[min(idx, len(self.model_names)-1)]
            try:
                if provider == "openai":
                    client = openai.OpenAI(api_key=api_key, base_url=api_base) if api_base else openai.OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_name or "gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        **kwargs
                    )
                    return response.choices[0].message.content
                elif provider == "anthropic":
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model=model_name or "claude-3-haiku-20240307",
                        max_tokens=512,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text
                else:
                    raise NotImplementedError(f"Provider '{provider}' ist nicht implementiert.")
            except Exception as e:
                last_error = str(e)
                print(f"[WARN] Fehler mit Provider {provider}: {e}")
                time.sleep(1)  # Warten, bevor der nächste probiert wird
                continue
        raise RuntimeError(f"Alle Modelle/Provider fehlgeschlagen: {last_error}")
