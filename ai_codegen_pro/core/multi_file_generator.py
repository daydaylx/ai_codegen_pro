"""Enterprise Multi-File Code Generator"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from ..utils.logger_service import LoggerService


@dataclass
class FileSpec:
    """Specification for a single file to generate"""

    filename: str
    template: str
    variables: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ProjectSpec:
    """Complete project specification"""

    name: str
    description: str
    files: List[FileSpec] = field(default_factory=list)
    project_variables: Dict[str, Any] = field(default_factory=dict)


class MultiFileGenerator:
    """Enterprise-grade multi-file code generator"""

    def __init__(self):
        self.logger = LoggerService().get_logger(__name__)
        self.project_templates = self._load_project_templates()

    def _load_project_templates(self) -> Dict[str, ProjectSpec]:
        """Load pre-defined project templates"""
        return {
            "fastapi_microservice": self._get_fastapi_microservice_spec(),
            "python_package": self._get_python_package_spec(),
        }

    def _get_fastapi_microservice_spec(self) -> ProjectSpec:
        """FastAPI microservice project template"""
        return ProjectSpec(
            name="FastAPI Microservice",
            description="Complete FastAPI microservice with database and tests",
            project_variables={
                "service_name": "MyService",
                "database": "sqlite",
                "authentication": True,
                "testing": True,
            },
            files=[
                FileSpec(
                    filename="main.py",
                    template="service_fastapi.j2",
                    description="FastAPI application entry point",
                    variables={"is_main": True},
                ),
                FileSpec(
                    filename="models.py",
                    template="pydantic_model.j2",
                    description="Pydantic models",
                    dependencies=[],
                ),
                FileSpec(
                    filename="requirements.txt",
                    template="",
                    description="Python dependencies",
                ),
                FileSpec(
                    filename="README.md",
                    template="markdown_doc.j2",
                    description="Project documentation",
                ),
            ],
        )

    def _get_python_package_spec(self) -> ProjectSpec:
        """Python package template"""
        return ProjectSpec(
            name="Python Package",
            description="Complete Python package with tests",
            project_variables={
                "package_name": "mypackage",
                "author": "Developer",
                "version": "0.1.0",
            },
            files=[
                FileSpec(
                    filename="__init__.py",
                    template="python_module.j2",
                    description="Package initialization",
                ),
                FileSpec(
                    filename="core.py",
                    template="python_module.j2",
                    description="Core functionality",
                ),
                FileSpec(
                    filename="test_core.py",
                    template="test.j2",
                    description="Tests",
                    dependencies=["core.py"],
                ),
                FileSpec(
                    filename="README.md",
                    template="markdown_doc.j2",
                    description="Documentation",
                ),
            ],
        )

    def list_project_types(self) -> List[str]:
        """Get available project types"""
        return list(self.project_templates.keys())

    def get_project_info(self, project_type: str) -> Optional[ProjectSpec]:
        """Get information about a project type"""
        return self.project_templates.get(project_type)

    def generate_project_structure(
        self, project_type: str, variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate project file structure"""
        if project_type not in self.project_templates:
            raise ValueError(f"Unknown project type: {project_type}")

        spec = self.project_templates[project_type]
        result = {}

        # Simple file generation
        for file_spec in spec.files:
            content = f"""# {file_spec.description}
# Generated for project: {variables.get('service_name', 'MyProject')}
# Template: {file_spec.template}

# TODO: Implement {file_spec.filename}
"""
            result[file_spec.filename] = content

        return result
