import zipfile
from pathlib import Path


def export_project_as_zip(files, output_zip_path: str):
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            temp_path = Path("/tmp") / file.name
            temp_path.write_text(file.content, encoding="utf-8")
            zipf.write(temp_path, arcname=file.name)
            temp_path.unlink()
