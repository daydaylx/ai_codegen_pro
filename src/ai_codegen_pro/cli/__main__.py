# ... (Der komplette Header/Rest bleibt wie in Phase 8!)
# Die generate_code-Funktion so anpassen:
@cli.command()
@click.option("--prompt", prompt="Prompt für die KI", help="Beschreibung der Funktion oder des Codes, den die KI generieren soll.")
@click.option("--provider", default=None, help="Kommagetrennte Provider-Liste: z.B. openai,openrouter,anthropic")
@click.option("--model", default=None, help="Kommagetrennte Modellnamen-Liste, Reihenfolge wie Provider")
@click.option("--api-key", default=None, help="Kommagetrennte API-Keys, Reihenfolge wie Provider")
@click.option("--api-base", default=None, help="Kommagetrennte API-Endpoints (nur bei OpenRouter etc.)")
@click.option("--out", default=None, help="Dateiname zum Speichern des KI-Outputs")
@click.option("--format", type=click.Choice(['plain', 'markdown', 'py']), default='plain', show_default=True, help="Ausgabeformat (plain/markdown/py)")
def generate_code(prompt, provider, model, api_key, api_base, out, format):
    """Lässt die KI Code generieren und gibt das Ergebnis aus (mit Fallback bei Fehlern)."""
    # Provider/Model/API-Listen parsen
    providers = [p.strip() for p in (provider or "openai").split(",")]
    models = [m.strip() for m in (model or "gpt-3.5-turbo").split(",")]
    api_keys = [k.strip() for k in (api_key or os.environ.get("AICODEGEN_API_KEY","")).split(",")]
    api_bases = [a.strip() for a in (api_base or os.environ.get("AICODEGEN_API_BASE","")).split(",")]
    router = ModelRouter(
        providers=providers,
        api_keys=api_keys,
        api_bases=api_bases,
        model_names=models
    )
    try:
        code = router.generate(prompt)
        # Formatieren und speichern wie gehabt ...
        if format == "markdown":
            out_str = f"```python\n{code}\n```"
        elif format == "py":
            out_str = code if code.strip().startswith("def ") or code.strip().startswith("class ") else f"# KI-Code\n{code}"
        else:
            out_str = code
        click.echo(out_str)
        if out:
            with open(out, "w", encoding="utf-8") as f:
                f.write(out_str)
            click.echo(f"\n[Gespeichert in {out}]")
        with open("history.log", "a", encoding="utf-8") as h:
            h.write(f"\n--- {datetime.now().isoformat()} ---\nPrompt: {prompt}\nProvider-Chain: {providers}\nModel-Chain: {models}\nAPI-Chain: {api_bases}\nOutput:\n{code}\n")
    except Exception as e:
        click.echo(f"Fehler bei der KI-Generierung (alle Modelle durch!): {e}")
