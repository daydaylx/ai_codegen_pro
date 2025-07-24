from ai_codegen_pro.core.template_service import TemplateService

def test_template_rendering():
    service = TemplateService()
    code = service.render("python_module.j2", {
        "module_docstring": "Testmodul",
        "function_name": "hello_world",
        "function_args": "",
        "function_docstring": "Gibt Hallo Welt aus."
    })
    assert "def hello_world" in code
