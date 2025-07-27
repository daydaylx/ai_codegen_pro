"""Plugin-System für AI CodeGen Pro"""

from .base import ModelPlugin, PluginBase, TemplatePlugin
from .manager import PluginManager
from .registry import PluginRegistry

__all__ = [
    "PluginBase",
    "TemplatePlugin",
    "ModelPlugin",
    "PluginManager",
    "PluginRegistry",
]
