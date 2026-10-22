"""Contexte d'exécution du graphe : paramètres statiques d'un run, hors état de la conversation."""
from dataclasses import dataclass, field

from ..config import require_env


@dataclass
class Context:
    # Par défaut, le modèle est lu dans la variable d'environnement MODEL_NAME ;
    # il peut être surchargé pour un run (Studio, API, tests) via `context={"model_name": ...}`.
    model_name: str = field(default_factory=lambda: require_env("MODEL_NAME"))
