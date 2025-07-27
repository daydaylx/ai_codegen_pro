"""
Unit tests for multi-file code generator.
"""

from unittest.mock import patch

import pytest

from ai_codegen_pro.core.multi_file_codegen import GeneratedFile, MultiFileCodeGenerator


class TestMultiFileCodeGenerator:
    @pytest.fixture
    def generator(self):
        with patch("ai_codegen_pro.core.multi_file_codegen.OpenRouterClient"):
            return MultiFileCodeGenerator("test-api-key")

    def test_generate_component_success(self, generator):
        generator.openrouter.generate_code.return_value = "def test():\n    pass"
        generator.model_router.select_model.return_value = "test-model"

        component = {
            "type": "module",
            "name": "test_module",
            "description": "Test module",
        }
        project_spec = {"type": "python"}

        result = generator._generate_component(component, project_spec)
        assert isinstance(result, GeneratedFile)
        assert result.name == "test_module.py"
        if result:
            assert "def test():" in result.content

    def test_generate_project_success(self, generator):
        generator.openrouter.generate_code.return_value = "# Generated code"
        generator.model_router.select_model.return_value = "test-model"

        project_spec = {
            "type": "python",
            "name": "test_project",
            "components": [{"type": "module", "name": "main", "description": "Main module"}],
        }

        result = generator.generate_project(project_spec)
        assert result.success
        assert len(result.files) == 1
        assert result.files[0].name == "main.py"
