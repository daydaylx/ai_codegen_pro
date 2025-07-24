import click

@click.group()
def cli():
    """ai_codegen_pro: KI-gestütztes Codegenerierungstool"""

@cli.command()
def hello():
    """Testkommando."""
    click.echo("Hello from ai_codegen_pro!")

if __name__ == "__main__":
    cli()
