import logging
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateError
from pathlib import Path

class TemplateService:
    def __init__(self, template_dir=None, filters=None, extensions=None):
        self.template_dir = template_dir or str(Path(__file__).parent.parent / "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        if filters:
            for name, func in filters.items():
                self.env.filters[name] = func
        if extensions:
            for ext in extensions:
                self.env.add_extension(ext)

    def render(self, template_name, context):
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            logging.error(f"Template '{template_name}' nicht gefunden im Ordner '{self.template_dir}'")
            raise FileNotFoundError(f"Template '{template_name}' nicht gefunden!")
        except TemplateError as e:
            logging.error(f"Template-Fehler: {e}")
            raise
        except Exception as e:
            logging.error(f"Unbekannter Fehler beim Rendern: {e}")
            raise

    def list_templates(self):
        return self.env.list_templates()
