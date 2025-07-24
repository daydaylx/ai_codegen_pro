import os
import click
from datetime import datetime
from ai_codegen_pro.core.template_service import TemplateService
from ai_codegen_pro.core.model_router import ModelRouter

@click.group()
def cli():
    """ai_codegen_pro: KI-gestütztes Codegenerierungstool"""

@cli.command()
@click.option("--modulname", prompt="Modulname", help="Name des Moduls/Funktions.")
@click.option("--funktion", prompt="Funktionsname", help="Name der zu generierenden Funktion.")
@click.option("--doc", prompt="Funktionsbeschreibung", help="Beschreibung der Funktion.")
def render_template(modulname, funktion, doc):
    """Erstellt ein Python-Modul aus dem Template und gibt es aus."""
    service = TemplateService()
    code = service.render("python_module.j2", {
        "module_docstring": modulname,
        "function_name": funktion,
        "function_args": "",
        "function_docstring": doc,
    })
    click.echo(code)

@cli.command()
@click.option("--prompt", prompt="Prompt für die KI", help="Beschreibung der Funktion oder des Codes, den die KI generieren soll.")
@click.option("--provider", default=lambda: os.environ.get("AICODEGEN_PROVIDER", "openai"), show_default="openai", help="KI-Anbieter: openai, openrouter, anthropic")
@click.option("--model", default=None, help="Modellname (optional, z.B. gpt-4, mistral-7b, claude-3-haiku)")
@click.option("--api-key", default=lambda: os.environ.get("AICODEGEN_API_KEY", ""), help="API-Key für das gewählte Modell (kann auch als Umgebungsvariable gesetzt werden)")
@click.option("--api-base", default=lambda: os.environ.get("AICODEGEN_API_BASE", None), help="(Optional) Eigener API-Endpoint, z.B. für OpenRouter")
@click.option("--out", default=None, help="Dateiname zum Speichern des KI-Outputs")
@click.option("--format", type=click.Choice(['plain', 'markdown', 'py']), default='plain', show_default=True, help="Ausgabeformat (plain/markdown/py)")
def generate_code(prompt, provider, model, api_key, api_base, out, format):
    """Lässt die KI Code generieren und gibt das Ergebnis aus (und speichert es optional)."""
    if not api_key:
        click.echo("FEHLER: Kein API-Key angegeben! Bitte Option --api-key oder Umgebungsvariable AICODEGEN_API_KEY setzen.")
        return
    router = ModelRouter(
        provider=provider,
        api_key=api_key,
        api_base=api_base,
        model_name=model
    )
    try:
        code = router.generate(prompt)
        # Formatieren
        if format == "markdown":
            out_str = f"```python\n{code}\n```"
        elif format == "py":
            out_str = code if code.strip().startswith("def ") or code.strip().startswith("class ") else f"# KI-Code\n{code}"
        else:
            out_str = code
        click.echo(out_str)
        # In Datei speichern, falls gewünscht
        if out:
            with open(out, "w", encoding="utf-8") as f:
                f.write(out_str)
            click.echo(f"\n[Gespeichert in {out}]")
        # Verlauf anhängen
        with open("history.log", "a", encoding="utf-8") as h:
            h.write(f"\n--- {datetime.now().isoformat()} ---\nPrompt: {prompt}\nModel: {model}\nProvider: {provider}\nAPI: {api_base}\nOutput:\n{code}\n")
    except Exception as e:
        click.echo(f"Fehler bei der KI-Generierung: {e}")

@cli.command()
def hello():
    """Testkommando."""
    click.echo("Hello from ai_codegen_pro!")

if __name__ == "__main__":
    cli()
