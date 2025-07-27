"""Model Router for selecting optimal AI models"""

from typing import List, Optional
from ..utils.logger_service import LoggerService


class ModelRouter:
    """Routes requests to optimal AI models based on task type"""

    def __init__(self):
        self.logger = LoggerService().get_logger(__name__)
        self.model_preferences = {
            "code_generation": ["openai/gpt-4-turbo", "anthropic/claude-3-opus"],
            "documentation": ["openai/gpt-3.5-turbo", "anthropic/claude-3-sonnet"],
            "refactoring": ["openai/gpt-4", "anthropic/claude-3-opus"],
        }

    def get_optimal_model(
        self, task_type: str, available_models: List[str]
    ) -> Optional[str]:
        """Select optimal model for task"""
        preferred = self.model_preferences.get(task_type, [])

        for model in preferred:
            if model in available_models:
                return model

        # Fallback to first available
        return available_models[0] if available_models else None
