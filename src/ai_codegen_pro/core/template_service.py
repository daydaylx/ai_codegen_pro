from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class TemplateService:
    """
    Verwaltet das Laden und Rendern von Templates für Modulerzeugung.
    """

    def __init__(self, template_dir=None):
        self.template_dir = template_dir or str(Path(__file__).parent.parent / "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def render(self, template_name, context):
        """
        Rendert ein Template mit dem angegebenen Kontext.
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
