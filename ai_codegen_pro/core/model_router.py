"""Model-Router für intelligente Model-Auswahl basierend auf Task-Typ"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

from ..utils.logger_service import LoggerService


class TaskType(Enum):
    """Verschiedene Task-Typen für Model-Routing"""

    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_EXPLANATION = "code_explanation"
    CODE_REFACTORING = "code_refactoring"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    GENERAL = "general"


class ModelCapability(Enum):
    """Model-Fähigkeiten"""

    CODING = "coding"
    REASONING = "reasoning"
    CREATIVITY = "creativity"
    SPEED = "speed"
    CONTEXT_LENGTH = "context_length"
    COST_EFFICIENCY = "cost_efficiency"


class ModelInfo:
    """Informationen über ein KI-Modell"""

    def __init__(
        self,
        name: str,
        provider: str,
        capabilities: Dict[ModelCapability, float],
        context_length: int,
        cost_per_token: float,
        speed_score: float,
        recommended_tasks: List[TaskType],
    ) -> None:
        self.name: str = name
        self.provider: str = provider
        self.capabilities: Dict[ModelCapability, float] = capabilities
        self.context_length: int = context_length
        self.cost_per_token: float = cost_per_token
        self.speed_score: float = speed_score
        self.recommended_tasks: List[TaskType] = recommended_tasks


class ModelRouter:
    """Router für intelligente Model-Auswahl"""

    def __init__(self) -> None:
        self.logger = LoggerService().get_logger(__name__)
        self.models: Dict[str, ModelInfo] = self._initialize_models()

        self.logger.debug(f"ModelRouter initialisiert mit {len(self.models)} Modellen")

    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Initialisiert die Model-Datenbank"""
        models: Dict[str, ModelInfo] = {}

        # OpenAI Models
        models["openai/gpt-4-turbo"] = ModelInfo(
            name="openai/gpt-4-turbo",
            provider="openai",
            capabilities={
                ModelCapability.CODING: 0.95,
                ModelCapability.REASONING: 0.9,
                ModelCapability.CREATIVITY: 0.8,
                ModelCapability.SPEED: 0.7,
                ModelCapability.CONTEXT_LENGTH: 0.9,
                ModelCapability.COST_EFFICIENCY: 0.6,
            },
            context_length=128000,
            cost_per_token=0.00003,
            speed_score=0.7,
            recommended_tasks=[
                TaskType.CODE_GENERATION,
                TaskType.CODE_REVIEW,
                TaskType.ARCHITECTURE,
                TaskType.DEBUGGING,
            ],
        )

        models["openai/gpt-4"] = ModelInfo(
            name="openai/gpt-4",
            provider="openai",
            capabilities={
                ModelCapability.CODING: 0.9,
                ModelCapability.REASONING: 0.95,
                ModelCapability.CREATIVITY: 0.85,
                ModelCapability.SPEED: 0.5,
                ModelCapability.CONTEXT_LENGTH: 0.6,
                ModelCapability.COST_EFFICIENCY: 0.4,
            },
            context_length=8192,
            cost_per_token=0.00006,
            speed_score=0.5,
            recommended_tasks=[
                TaskType.CODE_REVIEW,
                TaskType.ARCHITECTURE,
                TaskType.CODE_EXPLANATION,
            ],
        )

        models["openai/gpt-3.5-turbo"] = ModelInfo(
            name="openai/gpt-3.5-turbo",
            provider="openai",
            capabilities={
                ModelCapability.CODING: 0.7,
                ModelCapability.REASONING: 0.7,
                ModelCapability.CREATIVITY: 0.6,
                ModelCapability.SPEED: 0.9,
                ModelCapability.CONTEXT_LENGTH: 0.7,
                ModelCapability.COST_EFFICIENCY: 0.9,
            },
            context_length=16385,
            cost_per_token=0.000002,
            speed_score=0.9,
            recommended_tasks=[
                TaskType.CODE_GENERATION,
                TaskType.DOCUMENTATION,
                TaskType.GENERAL,
            ],
        )

        # Anthropic Models
        models["anthropic/claude-3-opus"] = ModelInfo(
            name="anthropic/claude-3-opus",
            provider="anthropic",
            capabilities={
                ModelCapability.CODING: 0.9,
                ModelCapability.REASONING: 0.95,
                ModelCapability.CREATIVITY: 0.9,
                ModelCapability.SPEED: 0.6,
                ModelCapability.CONTEXT_LENGTH: 0.95,
                ModelCapability.COST_EFFICIENCY: 0.3,
            },
            context_length=200000,
            cost_per_token=0.000075,
            speed_score=0.6,
            recommended_tasks=[
                TaskType.CODE_REVIEW,
                TaskType.ARCHITECTURE,
                TaskType.CODE_REFACTORING,
            ],
        )

        models["anthropic/claude-3-sonnet"] = ModelInfo(
            name="anthropic/claude-3-sonnet",
            provider="anthropic",
            capabilities={
                ModelCapability.CODING: 0.85,
                ModelCapability.REASONING: 0.9,
                ModelCapability.CREATIVITY: 0.8,
                ModelCapability.SPEED: 0.8,
                ModelCapability.CONTEXT_LENGTH: 0.95,
                ModelCapability.COST_EFFICIENCY: 0.7,
            },
            context_length=200000,
            cost_per_token=0.000015,
            speed_score=0.8,
            recommended_tasks=[
                TaskType.CODE_GENERATION,
                TaskType.CODE_EXPLANATION,
                TaskType.DEBUGGING,
            ],
        )

        models["anthropic/claude-3-haiku"] = ModelInfo(
            name="anthropic/claude-3-haiku",
            provider="anthropic",
            capabilities={
                ModelCapability.CODING: 0.7,
                ModelCapability.REASONING: 0.75,
                ModelCapability.CREATIVITY: 0.6,
                ModelCapability.SPEED: 0.95,
                ModelCapability.CONTEXT_LENGTH: 0.95,
                ModelCapability.COST_EFFICIENCY: 0.95,
            },
            context_length=200000,
            cost_per_token=0.00000025,
            speed_score=0.95,
            recommended_tasks=[
                TaskType.CODE_GENERATION,
                TaskType.DOCUMENTATION,
                TaskType.TESTING,
            ],
        )

        # Code-spezialisierte Models
        models["codellama/codellama-34b-instruct"] = ModelInfo(
            name="codellama/codellama-34b-instruct",
            provider="meta",
            capabilities={
                ModelCapability.CODING: 0.9,
                ModelCapability.REASONING: 0.7,
                ModelCapability.CREATIVITY: 0.6,
                ModelCapability.SPEED: 0.8,
                ModelCapability.CONTEXT_LENGTH: 0.8,
                ModelCapability.COST_EFFICIENCY: 0.8,
            },
            context_length=16384,
            cost_per_token=0.000001,
            speed_score=0.8,
            recommended_tasks=[
                TaskType.CODE_GENERATION,
                TaskType.CODE_REFACTORING,
                TaskType.DEBUGGING,
            ],
        )

        return models

    def recommend_model(
        self,
        task_type: TaskType,
        priority_capabilities: Optional[List[ModelCapability]] = None,
        max_cost_per_token: Optional[float] = None,
        min_context_length: Optional[int] = None,
        min_speed_score: Optional[float] = None,
    ) -> Tuple[str, float]:
        """
        Empfiehlt das beste Modell für einen Task

        Args:
            task_type: Art der Aufgabe
            priority_capabilities: Wichtige Fähigkeiten (optional)
            max_cost_per_token: Maximale Kosten pro Token (optional)
            min_context_length: Minimale Context-Length (optional)
            min_speed_score: Minimaler Speed-Score (optional)

        Returns:
            Tuple mit (model_name, confidence_score)
        """
        candidates: List[Tuple[str, float]] = []

        for model_name, model_info in self.models.items():
            # Filter anwenden
            if max_cost_per_token and model_info.cost_per_token > max_cost_per_token:
                continue

            if min_context_length and model_info.context_length < min_context_length:
                continue

            if min_speed_score and model_info.speed_score < min_speed_score:
                continue

            # Score berechnen
            score: float = self._calculate_model_score(
                model_info, task_type, priority_capabilities
            )

            candidates.append((model_name, score))

        if not candidates:
            # Fallback auf bestes verfügbares Modell
            self.logger.warning(
                "Keine Modelle erfüllen die Kriterien, verwende Fallback"
            )
            return "openai/gpt-4-turbo", 0.5

        # Bestes Modell zurückgeben
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_model, confidence = candidates[0]

        self.logger.info(f"Error loading model {model_name}: ")
        return best_model, confidence

    def _calculate_model_score(
        self,
        model_info: ModelInfo,
        task_type: TaskType,
        priority_capabilities: Optional[List[ModelCapability]],
    ) -> float:
        """
        Berechnet einen Score für ein Modell basierend auf Task und Anforderungen

        Args:
            model_info: Model-Informationen
            task_type: Art der Aufgabe
            priority_capabilities: Wichtige Fähigkeiten

        Returns:
            Score zwischen 0 und 1
        """
        score: float = 0.0

        # Task-spezifischer Bonus
        if task_type in model_info.recommended_tasks:
            score += 0.3

        # Capability-basierter Score
        capability_weights: Dict[ModelCapability, float] = {
            ModelCapability.CODING: 0.4,
            ModelCapability.REASONING: 0.3,
            ModelCapability.CREATIVITY: 0.1,
            ModelCapability.SPEED: 0.1,
            ModelCapability.CONTEXT_LENGTH: 0.05,
            ModelCapability.COST_EFFICIENCY: 0.05,
        }

        # Task-spezifische Gewichtungen
        if task_type == TaskType.CODE_GENERATION:
            capability_weights[ModelCapability.CODING] = 0.5
            capability_weights[ModelCapability.CREATIVITY] = 0.2
        elif task_type == TaskType.CODE_REVIEW:
            capability_weights[ModelCapability.REASONING] = 0.4
            capability_weights[ModelCapability.CODING] = 0.4
        elif task_type == TaskType.DEBUGGING:
            capability_weights[ModelCapability.REASONING] = 0.5
            capability_weights[ModelCapability.CODING] = 0.3
        elif task_type == TaskType.DOCUMENTATION:
            capability_weights[ModelCapability.CREATIVITY] = 0.3
            capability_weights[ModelCapability.SPEED] = 0.2
            capability_weights[ModelCapability.COST_EFFICIENCY] = 0.2

        # Priority capabilities höher gewichten
        if priority_capabilities:
            for capability in priority_capabilities:
                if capability in capability_weights:
                    capability_weights[capability] *= 1.5

        # Normalisieren
        total_weight: float = sum(capability_weights.values())
        capability_weights = {
            k: v / total_weight for k, v in capability_weights.items()
        }

        # Score berechnen
        for capability, weight in capability_weights.items():
            if capability in model_info.capabilities:
                score += model_info.capabilities[capability] * weight

        return min(1.0, score)

    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """
        Gibt Model-Informationen zurück

        Args:
            model_name: Name des Modells

        Returns:
            ModelInfo oder None wenn nicht gefunden
        """
        return self.models.get(model_name)

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        """
        Listet verfügbare Modelle auf

        Args:
            provider: Filter nach Provider (optional)

        Returns:
            Liste der Model-Namen
        """
        if provider:
            return [
                name for name, info in self.models.items() if info.provider == provider
            ]
        return list(self.models.keys())

    def get_providers(self) -> List[str]:
        """
        Gibt verfügbare Provider zurück

        Returns:
            Liste der Provider
        """
        providers: set[str] = {info.provider for info in self.models.values()}
        return sorted(list(providers))

    def compare_models(self, model_names: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Vergleicht mehrere Modelle

        Args:
            model_names: Liste der zu vergleichenden Modelle

        Returns:
            Dictionary mit Vergleichsdaten
        """
        comparison: Dict[str, Dict[str, float]] = {}

        for model_name in model_names:
            if model_name in self.models:
                model_info: ModelInfo = self.models[model_name]
                comparison[model_name] = {
                    "coding": model_info.capabilities.get(ModelCapability.CODING, 0),
                    "reasoning": model_info.capabilities.get(
                        ModelCapability.REASONING, 0
                    ),
                    "speed": model_info.speed_score,
                    "cost_efficiency": model_info.capabilities.get(
                        ModelCapability.COST_EFFICIENCY, 0
                    ),
                    "context_length": model_info.context_length,
                    "cost_per_token": model_info.cost_per_token,
                }

        return comparison
