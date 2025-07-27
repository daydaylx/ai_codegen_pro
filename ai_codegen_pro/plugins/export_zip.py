from ai_codegen_pro.plugins.base import CodeGenPlugin
from ai_codegen_pro.utils import exporter


class ZipExportPlugin(CodeGenPlugin):
    def on_post_generate(self, files, result):
        output_zip = "./exported_project.zip"
        exporter.export_project_as_zip(files, output_zip)
        print(f"Projekt als ZIP exportiert: {output_zip}")
