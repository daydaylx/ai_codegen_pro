"""Template-Service für Jinja2-basierte Code-Templates"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError

from ..utils.logger_service import LoggerService


class TemplateServiceError(Exception):
    """Template-Service spezifische Fehlerklasse"""

    pass


class TemplateService:
    """Service für die Verwaltung und Verarbeitung von Code-Templates"""

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialisiert den Template-Service

        Args:
            templates_dir: Pfad zum Templates-Verzeichnis (optional)
        """
        self.logger = LoggerService().get_logger(__name__)

        # Templates-Verzeichnis bestimmen
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Standard: templates/ Verzeichnis im Package
            package_dir = Path(__file__).parent.parent
            self.templates_dir = package_dir / "templates"

        # Prüfen ob Templates-Verzeichnis existiert
        if not self.templates_dir.exists():
            self.logger.warning(
                f"Templates-Verzeichnis nicht gefunden: {self.templates_dir}"
            )
            # Verzeichnis erstellen falls es nicht existiert
            try:
                self.templates_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(
                    f"Templates-Verzeichnis erstellt: {self.templates_dir}"
                )
            except Exception as e:
                raise TemplateServiceError(
                    f"Konnte Templates-Verzeichnis nicht erstellen: {e}"
                )

        # Jinja2 Environment konfigurieren
        try:
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=False,  # Für Code-Templates nicht escapen
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )

            # Custom Filters hinzufügen
            self.env.filters["snake_case"] = self._to_snake_case
            self.env.filters["camel_case"] = self._to_camel_case
            self.env.filters["pascal_case"] = self._to_pascal_case

            self.logger.debug(
                f"Template-Service initialisiert mit Verzeichnis: {self.templates_dir}"
            )

        except Exception as e:
            raise TemplateServiceError(f"Fehler bei der Jinja2-Initialisierung: {e}")

    def list_templates(self) -> List[str]:
        """
        Listet alle verfügbaren Templates auf

        Returns:
            Liste der Template-Dateinamen
        """
        try:
            templates = []
            for template_file in self.templates_dir.glob("*.j2"):
                templates.append(template_file.name)

            self.logger.debug(f"Gefundene Templates: {templates}")
            return templates

        except Exception as e:
            self.logger.error(f"Fehler beim Auflisten der Templates: {e}")
            raise TemplateServiceError(f"Konnte Templates nicht auflisten: {e}")

    def get_template(self, template_name: str) -> str:
        """
        Lädt den Inhalt eines Templates

        Args:
            template_name: Name der Template-Datei

        Returns:
            Template-Inhalt als String

        Raises:
            TemplateServiceError: Wenn Template nicht gefunden oder fehlerhaft
        """
        try:
            template = self.env.get_template(template_name)
            content = template.source

            self.logger.debug(f"Template geladen: {template_name}")
            return content

        except TemplateNotFound:
            error_msg = f"Template nicht gefunden: {template_name}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

        except TemplateSyntaxError as e:
            error_msg = f"Syntax-Fehler in Template {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

        except Exception as e:
            error_msg = f"Fehler beim Laden des Templates {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Rendert ein Template mit den gegebenen Variablen

        Args:
            template_name: Name der Template-Datei
            variables: Dictionary mit Template-Variablen

        Returns:
            Gerenderte Template als String

        Raises:
            TemplateServiceError: Wenn Template nicht gefunden oder Render-Fehler
        """
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**variables)

            self.logger.debug(
                f"Template gerendert: {template_name} mit {len(variables)} Variablen"
            )
            return rendered

        except TemplateNotFound:
            error_msg = f"Template nicht gefunden: {template_name}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

        except TemplateSyntaxError as e:
            error_msg = f"Syntax-Fehler in Template {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

        except Exception as e:
            error_msg = f"Fehler beim Rendern des Templates {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

    def template_exists(self, template_name: str) -> bool:
        """
        Prüft ob ein Template existiert

        Args:
            template_name: Name der Template-Datei

        Returns:
            True wenn Template existiert, False sonst
        """
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False
        except Exception as e:
            self.logger.warning(
                f"Fehler beim Prüfen des Templates {template_name}: {e}"
            )
            return False

    def create_template(self, template_name: str, content: str) -> None:
        """
        Erstellt ein neues Template

        Args:
            template_name: Name der neuen Template-Datei
            content: Template-Inhalt

        Raises:
            TemplateServiceError: Wenn Template nicht erstellt werden kann
        """
        try:
            template_path = self.templates_dir / template_name

            # Prüfen ob Template bereits existiert
            if template_path.exists():
                self.logger.warning(f"Template existiert bereits: {template_name}")

            # Template-Inhalt schreiben
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Jinja2 Environment neu laden
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )

            self.logger.info(f"Template erstellt: {template_name}")

        except Exception as e:
            error_msg = f"Fehler beim Erstellen des Templates {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

    def delete_template(self, template_name: str) -> None:
        """
        Löscht ein Template

        Args:
            template_name: Name der zu löschenden Template-Datei

        Raises:
            TemplateServiceError: Wenn Template nicht gelöscht werden kann
        """
        try:
            template_path = self.templates_dir / template_name

            if not template_path.exists():
                error_msg = f"Template nicht gefunden: {template_name}"
                self.logger.error(error_msg)
                raise TemplateServiceError(error_msg)

            template_path.unlink()

            # Jinja2 Environment neu laden
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )

            self.logger.info(f"Template gelöscht: {template_name}")

        except Exception as e:
            error_msg = f"Fehler beim Löschen des Templates {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Gibt Informationen über ein Template zurück

        Args:
            template_name: Name der Template-Datei

        Returns:
            Dictionary mit Template-Informationen

        Raises:
            TemplateServiceError: Wenn Template nicht gefunden
        """
        try:
            template_path = self.templates_dir / template_name

            if not template_path.exists():
                error_msg = f"Template nicht gefunden: {template_name}"
                self.logger.error(error_msg)
                raise TemplateServiceError(error_msg)

            stat = template_path.stat()

            info = {
                "name": template_name,
                "path": str(template_path),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "exists": True,
            }

            self.logger.debug(f"Template-Info abgerufen: {template_name}")
            return info

        except Exception as e:
            error_msg = f"Fehler beim Abrufen der Template-Info {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateServiceError(error_msg)

    # Custom Jinja2 Filter
    @staticmethod
    def _to_snake_case(text: str) -> str:
        """Konvertiert Text zu snake_case"""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def _to_camel_case(text: str) -> str:
        """Konvertiert Text zu camelCase"""
        components = text.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    @staticmethod
    def _to_pascal_case(text: str) -> str:
        """Konvertiert Text zu PascalCase"""
        components = text.split("_")
        return "".join(x.title() for x in components)

    def get_plugin_templates(self) -> Dict[str, str]:
        """
        Sammelt alle Templates von aktiven Plugins

        Returns:
            Dict mit {template_name: template_content}
        """
        plugin_templates = {}

        try:
            from ..plugins.manager import PluginManager

            plugin_manager = PluginManager()

            plugin_templates = plugin_manager.get_all_templates()
            self.logger.debug(f"Plugin-Templates geladen: {len(plugin_templates)}")

        except Exception as e:
            self.logger.error(f"Fehler beim Laden von Plugin-Templates: {e}")

        return plugin_templates

    def list_all_templates(self) -> List[str]:
        """
        Listet alle Templates auf (Standard + Plugin)

        Returns:
            Liste aller Template-Namen
        """
        # Standard-Templates
        standard_templates = self.list_templates()

        # Plugin-Templates
        plugin_templates = list(self.get_plugin_templates().keys())

        # Kombinieren und sortieren
        all_templates = standard_templates + plugin_templates
        return sorted(all_templates)

    def get_template_with_plugins(self, template_name: str) -> str:
        """
        Lädt Template (Standard oder Plugin)

        Args:
            template_name: Template-Name

        Returns:
            Template-Inhalt

        Raises:
            TemplateServiceError: Wenn Template nicht gefunden
        """
        # Erst in Standard-Templates suchen
        try:
            return self.get_template(template_name)
        except TemplateServiceError:
            pass

        # Dann in Plugin-Templates suchen
        plugin_templates = self.get_plugin_templates()

        if template_name in plugin_templates:
            return plugin_templates[template_name]

        # Nicht gefunden
        raise TemplateServiceError(f"Template nicht gefunden: {template_name}")
