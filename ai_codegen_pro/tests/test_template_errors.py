import pytest
from ai_codegen_pro.core.template_service import TemplateService

def test_template_not_found():
    service = TemplateService()
    with pytest.raises(FileNotFoundError):
        service.render("nicht_existierend.j2", {})
