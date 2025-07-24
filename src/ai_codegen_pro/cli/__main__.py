import click
from ai_codegen_pro.core.template_service import TemplateService

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
def hello():
    """Testkommando."""
    click.echo("Hello from ai_codegen_pro!")

if __name__ == "__main__":
    cli()
