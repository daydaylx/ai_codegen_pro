"""Tests für Multi-File Code Generation"""

import pytest

from ..core.multi_file_generator import MultiFileGenerator, ProjectSpec


class TestMultiFileGenerator:
    """Test-Suite für MultiFileGenerator"""

    def test_init(self):
        """Test Generator-Initialisierung"""
        generator = MultiFileGenerator()
        assert generator is not None
        assert hasattr(generator, "project_templates")

    def test_list_project_types(self):
        """Test Auflistung verfügbarer Projekt-Typen"""
        generator = MultiFileGenerator()
        types = generator.list_project_types()

        assert isinstance(types, list)
        assert len(types) > 0
        assert "fastapi_microservice" in types

    def test_get_project_info(self):
        """Test Abrufen von Projekt-Informationen"""
        generator = MultiFileGenerator()
        info = generator.get_project_info("fastapi_microservice")

        assert isinstance(info, ProjectSpec)
        assert info.name == "FastAPI Microservice"
        assert len(info.files) > 0

    def test_generate_project_structure(self):
        """Test Projekt-Struktur-Generierung"""
        generator = MultiFileGenerator()
        variables = {"service_name": "TestService"}

        files = generator.generate_project_structure("fastapi_microservice", variables)

        assert isinstance(files, dict)
        assert len(files) > 0
        assert "main.py" in files
        assert "TestService" in files["main.py"]

    def test_invalid_project_type(self):
        """Test ungültiger Projekt-Typ"""
        generator = MultiFileGenerator()

        with pytest.raises(ValueError):
            generator.generate_project_structure("invalid_type", {})
