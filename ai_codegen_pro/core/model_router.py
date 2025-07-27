"""
Model Router to select AI model based on task type.
"""


class ModelRouter:
    def __init__(self):
        self.model_map = {
            "module": "anthropic/claude-3-sonnet-20240229",
            "service": "openai/gpt-4o-mini",
            "model": "anthropic/claude-3-sonnet-20240229",
            "test": "openai/gpt-3.5-turbo",
            "default": "openai/gpt-3.5-turbo",
        }

    def select_model(self, task_type: str) -> str:
        return self.model_map.get(task_type, self.model_map["default"])
