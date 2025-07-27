"""Template Service für Jinja2-Templates"""

from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..utils.logger_service import LoggerService


class TemplateServiceError(Exception):
    """Exception für Template-Service Fehler"""

    pass


class TemplateService:
    """Service für das Laden und Rendern von Jinja2-Templates"""

    def __init__(self, template_dir: str = None):
        self.logger = LoggerService().get_logger(__name__)

        if template_dir:
            self.template_dir = Path(template_dir)
        else:
            # Standard Template-Verzeichnis
            current_dir = Path(__file__).parent.parent
            self.template_dir = current_dir / "templates"

        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Jinja2 Environment einrichten
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        self.logger.debug(
            f"Template Service initialisiert mit Verzeichnis: " f"{self.template_dir}"
        )

    def get_plugin_templates(self) -> Dict[str, str]:
        """Sammelt alle Templates von aktiven Plugins"""
        plugin_templates = {}

        try:
            from ..plugins.manager import PluginManager

            plugin_manager = PluginManager()
            plugin_templates = plugin_manager.get_all_templates()
            self.logger.debug(f"Plugin-Templates geladen: {len(plugin_templates)}")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden von Plugin-Templates: {e}")

        return plugin_templates

    def list_templates(self) -> List[str]:
        """Listet alle verfügbaren Templates auf"""
        templates = []

        try:
            for template_file in self.template_dir.glob("*.j2"):
                templates.append(template_file.name)

            self.logger.debug(f"Gefundene Templates: {templates}")
            return sorted(templates)

        except Exception as e:
            self.logger.error(f"Fehler beim Auflisten der Templates: {e}")
            raise TemplateServiceError(f"Konnte Templates nicht auflisten: {e}")

    def get_template_with_plugins(self, template_name: str) -> str:
        """Lädt Template (Standard oder Plugin)"""
        # Erst in Standard-Templates suchen
        try:
            return self.get_template(template_name)
        except Exception:
            pass

        # Dann in Plugin-Templates suchen
        plugin_templates = self.get_plugin_templates()

        if template_name in plugin_templates:
            return plugin_templates[template_name]

        # Nicht gefunden
        raise Exception(f"Template nicht gefunden: {template_name}")

    def get_template(self, template_name: str) -> str:
        """Lädt ein Template und gibt den Inhalt zurück"""
        try:
            template_path = self.template_dir / template_name

            if not template_path.exists():
                raise TemplateServiceError(f"Template nicht gefunden: {template_name}")

            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.logger.debug(f"Template geladen: {template_name}")
            return content

        except Exception as e:
            self.logger.error(f"Fehler beim Laden des Templates {template_name}: {e}")
            raise TemplateServiceError(f"Konnte Template nicht laden: {e}")

    def render_template(self, template_name: str, variables: Dict = None) -> str:
        """Rendert ein Template mit den gegebenen Variablen"""
        if variables is None:
            variables = {}

        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**variables)

            self.logger.debug(
                f"Template gerendert: {template_name} "
                f"mit {len(variables)} Variablen"
            )
            return rendered

        except Exception as e:
            self.logger.error(f"Fehler beim Rendern des Templates {template_name}: {e}")
            raise TemplateServiceError(f"Konnte Template nicht rendern: {e}")

    def template_exists(self, template_name: str) -> bool:
        """Prüft ob ein Template existiert"""
        template_path = self.template_dir / template_name
        return template_path.exists()

    def create_template(self, template_name: str, content: str):
        """Erstellt ein neues Template"""
        try:
            template_path = self.template_dir / template_name

            with open(template_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Template erstellt: {template_name}")

        except Exception as e:
            self.logger.error(
                f"Fehler beim Erstellen des Templates {template_name}: {e}"
            )
            raise TemplateServiceError(f"Konnte Template nicht erstellen: {e}")
