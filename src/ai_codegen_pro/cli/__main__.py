import os
import click
from datetime import datetime
from ai_codegen_pro.core.template_service import TemplateService
from ai_codegen_pro.core.model_router import ModelRouter
import json

CONFIG_FILE = ".aicodegenrc"

def save_config(api_key, provider, api_base):
    config = {"api_key": api_key, "provider": provider, "api_base": api_base}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_api_credentials(provider_opt, api_key_opt, api_base_opt):
    config = load_config()
    api_key = api_key_opt or os.environ.get("AICODEGEN_API_KEY") or config.get("api_key")
    provider = provider_opt or os.environ.get("AICODEGEN_PROVIDER") or config.get("provider") or "openai"
    api_base = api_base_opt or os.environ.get("AICODEGEN_API_BASE") or config.get("api_base")
    if not api_key:
        api_key = click.prompt("Kein API-Key gefunden! Bitte gib deinen API-Key ein", hide_input=True)
        save_config(api_key, provider, api_base)
    return provider, api_key, api_base

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
@click.option("--provider", default=None, help="KI-Anbieter: openai, openrouter, anthropic")
@click.option("--model", default=None, help="Modellname (optional, z.B. gpt-4, mistral-7b, claude-3-haiku)")
@click.option("--api-key", default=None, help="API-Key für das gewählte Modell (kann auch als Umgebungsvariable oder in .aicodegenrc gespeichert werden)")
@click.option("--api-base", default=None, help="(Optional) Eigener API-Endpoint, z.B. für OpenRouter")
@click.option("--out", default=None, help="Dateiname zum Speichern des KI-Outputs")
@click.option("--format", type=click.Choice(['plain', 'markdown', 'py']), default='plain', show_default=True, help="Ausgabeformat (plain/markdown/py)")
def generate_code(prompt, provider, model, api_key, api_base, out, format):
    """Lässt die KI Code generieren und gibt das Ergebnis aus (und speichert es optional)."""
    provider, api_key, api_base = get_api_credentials(provider, api_key, api_base)
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
@click.option("--lines", default=10, help="Wie viele letzte Einträge anzeigen?")
def history(lines):
    """Zeigt die letzten Prompts & Outputs aus history.log."""
    if not os.path.exists("history.log"):
        click.echo("Noch keine History vorhanden.")
        return
    with open("history.log", "r", encoding="utf-8") as f:
        lines_content = f.readlines()[-lines:]
    click.echo("".join(lines_content))

@cli.command()
@click.argument("file")
def open_in_editor(file):
    """Öffnet eine Datei im Standard-Editor (z.B. VSCode, nano)."""
    editor = os.environ.get("EDITOR", "nano")
    os.system(f"{editor} {file}")

@cli.command()
def hello():
    """Testkommando."""
    click.echo("Hello from ai_codegen_pro!")

if __name__ == "__main__":
    cli()
