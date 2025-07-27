import json
import logging
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from ai_codegen_pro.core.template_service import TemplateService

log = logging.getLogger(__name__)


class MultiFileCodeGen:
    def __init__(self):
        self.template_service = TemplateService()

    def generate(self, raw_output: str) -> dict:
        try:
            files = json.loads(raw_output)
            if not isinstance(files, list):
                raise ValueError("KI-Output ist keine Liste.")
        except Exception as e:
            log.error(f"Ungültiges JSON-Format: {e}")
            return {}

        result = {}
        for item in files:
            try:
                fname = item.get("filename")
                tpl = item.get("template")
                context = item.get("context")
                if not (fname and tpl and context):
                    log.warning(f"Unvollständiger Eintrag: {item}")
                    continue
                code = self.template_service.render(tpl, context)
                result[fname] = code
            except Exception as e:
                log.error(f"Fehler bei {item}: {e}")
        return result

    def export_zip(self, file_dict: dict, zip_path: Path) -> bool:
        try:
            with ZipFile(zip_path, "w", ZIP_DEFLATED) as zipf:
                for fname, content in file_dict.items():
                    zipf.writestr(fname, content)
            log.info(f"ZIP exportiert nach {zip_path}")
            return True
        except Exception as e:
            log.error(f"ZIP-Export fehlgeschlagen: {e}")
            return False
