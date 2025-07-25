import json
import logging
from ai_codegen_pro.core.template_service import TemplateService

def parse_multi_file_response(raw_output):
    """
    Erwartet einen KI-Output wie:
    [
        {"filename": "foo.py", "template": "python_module.j2", "context": {"name": "foo", "body": "..."}},
        ...
    ]
    Liefert ein Dict: {filename: code, ...}
    """
    try:
        files = json.loads(raw_output)
        if not isinstance(files, list):
            raise ValueError("KI-Output ist keine Liste von Dateien.")
    except Exception as e:
        logging.error(f"KI-Output konnte nicht geparst werden: {e}")
        return {}

    tpl_service = TemplateService()
    result = {}
    for item in files:
        try:
            fname = item.get("filename")
            tpl = item.get("template")
            context = item.get("context")
            if not (fname and tpl and context):
                logging.warning(f"Unvollständiger File-Eintrag: {item}")
                continue
            code = tpl_service.render(tpl, context)
            result[fname] = code
        except Exception as e:
            logging.error(f"Fehler beim Rendern von {item}: {e}")
    return result

def export_zip(file_dict, zip_path):
    """
    file_dict: {filename: content}
    zip_path: Pfad zur .zip-Datei
    """
    from zipfile import ZipFile, ZIP_DEFLATED
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zipf:
        for fname, content in file_dict.items():
            zipf.writestr(fname, content)
