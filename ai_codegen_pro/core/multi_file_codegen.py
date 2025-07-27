"""
Multi-file code generator with real AI integration.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_codegen_pro.core.model_router import ModelRouter
from ai_codegen_pro.core.openrouter_client import OpenRouterClient, OpenRouterError
from ai_codegen_pro.core.template_service import TemplateService

logger = logging.getLogger(__name__)


@dataclass
class GeneratedFile:
    name: str
    content: str
    language: str
    template: str
    metadata: Dict[str, Any]


@dataclass
class GenerationResult:
    files: List[GeneratedFile]
    success: bool
    errors: List[str]
    total_tokens: int
    generation_time: float


class MultiFileCodeGenerator:
    def __init__(self, api_key: str):
        self.openrouter = OpenRouterClient(api_key)
        self.template_service = TemplateService()
        self.model_router = ModelRouter()

    def generate_project(
        self, project_spec: Dict[str, Any], output_dir: Optional[str] = None
    ) -> GenerationResult:
        start_time = time.time()
        files = []
        errors = []
        total_tokens = 0

        try:
            project_type = project_spec.get("type", "python")
            project_name = project_spec.get("name", "generated_project")
            components = project_spec.get("components", [])

            logger.info(f"Generating {project_type} project: {project_name}")

            for component in components:
                try:
                    file_result = self._generate_component(component, project_spec)
                    if file_result:
                        files.append(file_result)
                        total_tokens += file_result.metadata.get("tokens_used", 0)
                except Exception as exc:
                    error_msg = f"Failed to generate {component.get('name', 'unknown')}: {str(exc)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            if output_dir and files:
                self._save_files(files, output_dir)

        except Exception as exc:
            errors.append(f"Project generation failed: {str(exc)}")
            logger.error(f"Project generation failed: {exc}")

        generation_time = time.time() - start_time
        success = len(files) > 0 and not errors

        return GenerationResult(
            files=files,
            success=success,
            errors=errors,
            total_tokens=total_tokens,
            generation_time=generation_time,
        )

    def _generate_component(
        self,
        component: Dict[str, Any],
        project_spec: Dict[str, Any],
    ) -> Optional[GeneratedFile]:
        component_type = component.get("type", "module")
        file_name = component.get("name", "generated_file")
        description = component.get("description", "")

        model = self.model_router.select_model(component_type)
        template_name = self._get_template_for_component(component_type, project_spec.get("type"))
        prompt = self._create_generation_prompt(component, project_spec, template_name)

        try:
            generated_code = self.openrouter.generate_code(
                prompt=prompt,
                model=model,
                max_tokens=4000,
                temperature=0.1,
            )
            if template_name and self.template_service.template_exists(template_name):
                template_vars = self._extract_template_vars(component, generated_code)
                final_code = self.template_service.render_template(template_name, template_vars)
            else:
                final_code = generated_code

            file_extension = self._get_file_extension(component_type, project_spec.get("type"))
            full_name = file_name
            if not file_name.endswith(f".{file_extension}"):
                full_name = f"{file_name}.{file_extension}"

            return GeneratedFile(
                name=full_name,
                content=final_code,
                language=project_spec.get("type", "python"),
                template=template_name or "none",
                metadata={
                    "component_type": component_type,
                    "model_used": model,
                    "tokens_used": len(generated_code.split()) * 1.3,
                    "description": description,
                },
            )
        except OpenRouterError as exc:
            logger.error(f"AI generation failed for {file_name}: {exc}")
            raise

    def _create_generation_prompt(
        self,
        component: Dict[str, Any],
        project_spec: Dict[str, Any],
        template_name: Optional[str],
    ) -> str:
        project_type = project_spec.get("type", "python")
        component_type = component.get("type", "module")
        name = component.get("name", "component")
        description = component.get("description", "")
        requirements = component.get("requirements", [])

        prompt = f"""Generate a {project_type} {component_type} named '{name}'.

Description: {description}

Requirements:
"""
        for req in requirements:
            prompt += f"- {req}\n"

        prompt += "\nProject Context:\n"
        prompt += f"- Type: {project_type}\n"
        arch = project_spec.get("architecture", "standard")
        prompt += f"- Architecture: {arch}\n"
        prompt += "- Dependencies:\n"
        for dep in project_spec.get("dependencies", []):
            prompt += f"  - {dep}\n"
        prompt += "\n"

        prompt += (
            "Code Requirements:\n"
            "- Include comprehensive docstrings\n"
            "- Add type hints where applicable\n"
            "- Include error handling\n"
            f"- Follow best practices for {project_type}\n"
            "- Make code production-ready\n"
            "- Add logging where appropriate\n\n"
            "Generate ONLY the code, no explanations or markdown formatting.\n"
        )
        return prompt

    def _get_template_for_component(self, component_type: str, project_type: str) -> Optional[str]:
        template_map = {
            ("module", "python"): "python_module.j2",
            ("service", "python"): "service_fastapi.j2",
            ("model", "python"): "pydantic_model.j2",
            ("test", "python"): "unittest_pytest.j2",
            ("module", "node"): "node_module.j2",
            ("module", "go"): "go_module.j2",
            ("script", "bash"): "bash_script.j2",
            ("docker", None): "dockerfile.j2",
        }
        return template_map.get((component_type, project_type))

    def _get_file_extension(self, component_type: str, project_type: str) -> str:
        extension_map = {
            "python": "py",
            "node": "js",
            "go": "go",
            "bash": "sh",
            "docker": "Dockerfile",
        }
        if component_type == "docker":
            return "Dockerfile"
        return extension_map.get(project_type, "txt")

    def _extract_template_vars(
        self, component: Dict[str, Any], generated_code: str
    ) -> Dict[str, Any]:
        return {
            "name": component.get("name", "component"),
            "description": component.get("description", ""),
            "generated_code": generated_code,
            "imports": self._extract_imports(generated_code),
            "body": self._extract_body(generated_code),
        }

    def _extract_imports(self, code: str) -> str:
        lines = code.split("\n")
        imports = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")) and not stripped.startswith('"""'):
                imports.append(line)
        return "\n".join(imports)

    def _extract_body(self, code: str) -> str:
        lines = code.split("\n")
        body_lines = []
        skip_imports = True
        for line in lines:
            stripped = line.strip()
            if skip_imports and (stripped.startswith(("import ", "from ")) or stripped == ""):
                continue
            skip_imports = False
            body_lines.append(line)
        return "\n".join(body_lines)

    def _save_files(self, files: List[GeneratedFile], output_dir: str):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        for file in files:
            file_path = output_path / file.name
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file.content)
                logger.info(f"Saved {file.name} ({len(file.content)} chars)")
            except Exception as exc:
                logger.error(f"Failed to save {file.name}: {exc}")
