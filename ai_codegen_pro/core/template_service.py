"""
Template Service based on Jinja2 with custom filters.
"""

import logging

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)


def snake_case(value: str) -> str:
    import re

    value = re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()
    return value


def camel_case(value: str) -> str:
    components = value.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def pascal_case(value: str) -> str:
    components = value.split("_")
    return "".join(x.title() for x in components)


class TemplateService:
    def __init__(self, template_path: str = "ai_codegen_pro/templates"):
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.env.filters["snake_case"] = snake_case
        self.env.filters["camel_case"] = camel_case
        self.env.filters["pascal_case"] = pascal_case

    def template_exists(self, template_name: str) -> bool:
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False

    def render_template(self, template_name: str, context: dict) -> str:
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error for {template_name}: {e}")
            raise
