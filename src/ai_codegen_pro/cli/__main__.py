import os
import click
from datetime import datetime
from ai_codegen_pro.core.template_service import TemplateService
from ai_codegen_pro.core.model_router import ModelRouter
import json
from pathlib import Path

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

def smart_filename(prompt, step):
    """Gibt einen sinnvollen Dateinamen je nach Inhalt/Step zurück."""
    p = prompt.lower()
    if "architektur" in p or "overview" in p or "struktur" in p:
        return f"docs/architektur_step{step}.md"
    if "test" in p:
        return f"tests/test_step{step}.py"
    if "template" in p or "modul" in p or "funktion" in p or "code" in p:
        return f"src/generated_module_step{step}.py"
    return f"output_step{step}.txt"

@click.group()
def cli():
    """ai_codegen_pro: KI-gestütztes Codegenerierungstool"""

@cli.command()
@click.option("--steps", prompt="Wie viele Chain-Schritte (z.B. 2 oder 3)?", type=int, default=2)
@click.option("--first-prompt", prompt="Startprompt (z.B. Architekturvorschlag für Modul XY)", help="Der erste Prompt der Kette.")
@click.option("--model", default=None, help="Modellname (optional, für alle Steps gleich)")
def prompt_chain(steps, first_prompt, model):
    """
    Führt eine Prompt-Kette aus und speichert die Ergebnisse automatisch in passenden Dateien/Ordnern.
    """
    provider, api_key, api_base = get_api_credentials(None, None, None)
    router = ModelRouter(
        provider=provider,
        api_key=api_key,
        api_base=api_base,
        model_name=model
    )
    current_prompt = first_prompt
    chain_history = []
    for i in range(steps):
        click.echo(f"\n--- Schritt {i+1} ---")
        result = router.generate(current_prompt)
        click.echo(f"\n[Ergebnis]:\n{result}\n")
        chain_history.append({"step": i+1, "prompt": current_prompt, "output": result})
        # Datei bestimmen und ggf. Ordner anlegen
        fname = smart_filename(current_prompt, i+1)
        Path(os.path.dirname(fname)).mkdir(parents=True, exist_ok=True)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(result)
        click.echo(f"→ [Gespeichert als {fname}]")
        if i < steps-1:
            current_prompt = click.prompt(f"Prompt für Schritt {i+2} (z.B. 'Schreibe daraus jetzt ein Python-Modul')", default=result)
    # Chain-History loggen
    with open("chain_history.log", "a", encoding="utf-8") as ch:
        ch.write(json.dumps(chain_history, indent=2, ensure_ascii=False) + "\n")

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
