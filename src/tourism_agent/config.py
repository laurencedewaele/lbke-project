"""Lecture de la configuration de l'agent."""
import os

from .exceptions import ConfigurationError


def require_env(name: str) -> str:
    """Renvoie la variable d'environnement `name`, ou lève une ConfigurationError explicite."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigurationError(
            f"La variable d'environnement '{name}' n'est pas définie (voir .env.example)."
        )
    return value
