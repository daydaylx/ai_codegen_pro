"""CLI Interface für AI CodeGen Pro"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..core.openrouter_client import OpenRouterClient
from ..core.template_service import TemplateService
from ..utils.logger_service import LoggerService
from ..utils.settings_service import SettingsService


class CLIInterface:
    """Command Line Interface für AI CodeGen Pro"""

    def __init__(self):
        self.logger = LoggerService().get_logger(__name__)
        self.settings = SettingsService()
        self.template_service = TemplateService()

    def create_parser(self) -> argparse.ArgumentParser:
        """Argument Parser erstellen"""
        parser = argparse.ArgumentParser(
            description="AI CodeGen Pro - KI-basierte Codegenerierung",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument("--api-key", type=str, help="OpenRouter API Key")

        parser.add_argument(
            "--model",
            type=str,
            default="openai/gpt-4-turbo",
            help="KI-Model für Codegenerierung",
        )

        parser.add_argument(
            "--prompt", type=str, required=True, help="Prompt für Codegenerierung"
        )

        parser.add_argument(
            "--system-prompt", type=str, help="System-Prompt für das KI-Modell"
        )

        parser.add_argument(
            "--template", type=str, help="Template-Name für Codegenerierung"
        )

        parser.add_argument(
            "--output", type=Path, help="Ausgabedatei für generierten Code"
        )

        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Detaillierte Ausgabe"
        )

        parser.add_argument(
            "--list-templates",
            action="store_true",
            help="Verfügbare Templates auflisten",
        )

        parser.add_argument(
            "--list-models", action="store_true", help="Verfügbare Models auflisten"
        )

        return parser

    def run(self, args: Optional[list] = None) -> int:
        """CLI ausführen"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        try:
            if parsed_args.list_templates:
                return self._list_templates()

            if parsed_args.list_models:
                return self._list_models()

            return self._generate_code(parsed_args)

        except KeyboardInterrupt:
            print("\nAbgebrochen durch Benutzer")
            return 1
        except Exception as e:
            self.logger.error(f"CLI Fehler: {e}")
            print(f"Fehler: {e}")
            return 1

    def _list_templates(self) -> int:
        """Templates auflisten"""
        try:
            templates = self.template_service.list_all_templates()
            print("Verfügbare Templates:")
            for template in templates:
                name = template.replace(".j2", "")
                print(f"  - {name}")
            return 0
        except Exception as e:
            print(f"Fehler beim Laden der Templates: {e}")
            return 1

    def _list_models(self) -> int:
        """Models auflisten"""
        models = [
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",
        ]
        print("Verfügbare Models:")
        for model in models:
            print(f"  - {model}")
        return 0

    def _generate_code(self, args) -> int:
        """Code generieren"""
        api_key = args.api_key or self.settings.get("api_key")
        if not api_key:
            print("Fehler: API Key erforderlich")
            return 1

        try:
            client = OpenRouterClient(api_key)

            system_prompt = args.system_prompt or (
                "Du bist ein erfahrener Software-Entwickler. "
                "Erstelle sauberen, gut dokumentierten Code."
            )

            result = client.generate_code(
                model=args.model, prompt=args.prompt, system_prompt=system_prompt
            )

            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"Code gespeichert: {args.output}")
            else:
                print(result)

            return 0

        except Exception as e:
            print(f"Generierung fehlgeschlagen: {e}")
            return 1


def main():
    """CLI Hauptfunktion"""
    cli = CLIInterface()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
