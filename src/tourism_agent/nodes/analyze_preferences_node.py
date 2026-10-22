import logging

from ..schemas.state import State
from ..schemas.criteria import CriteriaIdentificationResult, StayType
from ..prompts.prompts import PREFERENCES_ANALYSIS_PROMPT_DICT, get_system_prompt
from ..llm import LLM_ERRORS, get_model
from ..schemas.context import Context
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime

logger = logging.getLogger(__name__)

# Définition d'une fonction d'analyse de préférences qui fusionne/enrichit l'état existant
def analyze_preferences_node(state: State, runtime: Runtime[Context]) -> dict:
    # Contexte par défaut (MODEL_NAME) si aucun contexte n'est fourni à l'appel du graphe
    model_name = (runtime.context or Context()).model_name

    # Récupération du prompt système pour le modèle spécifié
    # (ConfigurationError explicite si aucun prompt n'est défini pour ce modèle)
    system_prompt = get_system_prompt(PREFERENCES_ANALYSIS_PROMPT_DICT, model_name).format(
        list_staytype=StayType.infos()
    )

    # On analyse uniquement le dernier message reçu de l'utilisateur
    messages = state.get("messages") or []
    if not messages:
        logger.warning("Aucun message à analyser : critères inchangés")
        return {}
    user_message = messages[-1].text

    # Si des critères ont déjà été déterminés, on les ajoute
    query=f"Client: {user_message}"
    previous_criteria = state.get("criteria")
    if previous_criteria:
        query = f"Client: {user_message}\nEtat des préférences actuelles : {previous_criteria.as_dict()}"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    try:
        model_with_output = get_model(model_name).with_structured_output(CriteriaIdentificationResult)
        criteres = model_with_output.invoke(messages)
    except LLM_ERRORS:
        # Mode dégradé : on conserve les critères connus (ou aucun, ce qui mènera à une
        # demande de précisions) plutôt que de faire échouer toute la conversation
        logger.exception("Échec de l'analyse des préférences par le modèle '%s'", model_name)
        return {} if previous_criteria else {"criteria": CriteriaIdentificationResult()}

    if not isinstance(criteres, CriteriaIdentificationResult):
        logger.warning("Sortie structurée inattendue du modèle '%s' : %r", model_name, criteres)
        return {} if previous_criteria else {"criteria": CriteriaIdentificationResult()}

    return {"criteria": criteres}
