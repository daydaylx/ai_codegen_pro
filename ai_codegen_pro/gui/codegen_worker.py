"""Background worker for code generation"""

from PySide6.QtCore import QThread, Signal
from ..utils.logger_service import LoggerService


class CodeGenWorker(QThread):
    """Worker thread for code generation"""

    result_ready = Signal(str)
    error_occurred = Signal(str)
    progress_update = Signal(str)

    def __init__(self, api_key: str, model: str, prompt: str):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self.logger = LoggerService().get_logger(__name__)

    def run(self):
        """Run code generation"""
        try:
            self.progress_update.emit("Starting code generation")

            # Import here to avoid circular imports
            from ..core.openrouter_client import OpenRouterClient

            client = OpenRouterClient(self.api_key)
            result = client.generate_code(model=self.model, prompt=self.prompt)

            self.result_ready.emit(result)

        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            self.error_occurred.emit(str(e))
