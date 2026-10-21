"""Modèle de chat partagé par les nœuds du graphe."""

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Chargement des variables d'environnement
load_dotenv()

# Initialisation du modèle de chat avec OpenRouter
model = init_chat_model(
    model=os.environ["MODEL_NAME"],
    model_provider="openai",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0,
    # Sous `langgraph dev` (stream_mode "messages"), with_structured_output passe en
    # streaming et l'usage des tokens est perdu : LangSmith n'affiche alors aucun token.
    disable_streaming=True
)
