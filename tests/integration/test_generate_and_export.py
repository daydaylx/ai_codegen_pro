from ai_codegen_pro.core.multi_file_codegen import MultiFileCodeGenerator
from ai_codegen_pro.utils.exporter import export_project_as_zip


def test_generate_and_export_zip(tmp_path):
    gen = MultiFileCodeGenerator("dummy-key")
    gen.openrouter.generate_code = lambda **kwargs: "# test"
    gen.model_router.select_model = lambda x: "test"
    gen.template_service.render_template = lambda a, b: "# test"

    project_spec = {
        "type": "python",
        "name": "test",
        "components": [{"type": "module", "name": "main"}],
    }
    result = gen.generate_project(project_spec)
    assert result.success

    output_zip = tmp_path / "export.zip"
    export_project_as_zip(result.files, str(output_zip))
    assert output_zip.exists()
