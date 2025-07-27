"""Plugin-System für AI CodeGen Pro"""

from .base import PluginBase, TemplatePlugin, ModelPlugin
from .manager import PluginManager
from .registry import PluginRegistry

__all__ = [
    "PluginBase",
    "TemplatePlugin",
    "ModelPlugin",
    "PluginManager",
    "PluginRegistry",
]
