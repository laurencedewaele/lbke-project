import logging
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.runtime import Runtime
from ..schemas.context import Context
from ..llm import LLM_ERRORS, get_model
from ..schemas.state import State
from ..prompts.prompts import STAYS_PROPOSAL_PROMPT_DICT, get_system_prompt

logger = logging.getLogger(__name__)

def build_fallback_proposal(matching_stays: list[dict]) -> str:
    """Réponse construite sans LLM, utilisée lorsque le modèle est indisponible."""
    if not matching_stays:
        return ("Je rencontre un problème technique et ne trouve pas de séjour correspondant "
                "à vos critères pour le moment. Pourriez-vous réessayer dans quelques instants ?")
    stays = "\n".join(f"- {stay['nom']} (correspondance {stay['match']})" for stay in matching_stays)
    return ("Je rencontre un problème technique pour détailler ma proposition, mais voici "
            f"les séjours de notre catalogue qui correspondent à vos critères :\n\n{stays}")


def respond_with_proposal_node(state: State, runtime: Runtime[Context]) -> dict:
    # Contexte par défaut (MODEL_NAME) si aucun contexte n'est fourni à l'appel du graphe
    model_name = (runtime.context or Context()).model_name

    # Récupération du prompt système pour le modèle spécifié
    # (ConfigurationError explicite si aucun prompt n'est défini pour ce modèle)
    criteria = state.get("criteria")
    matching_stays = state.get("matching_stays") or []
    system_prompt = get_system_prompt(STAYS_PROPOSAL_PROMPT_DICT, model_name) + \
                    f"\nCritères actuels : {criteria.as_dict() if criteria else {}}" + \
                    f"\nSéjours correspondants du catalogue : {matching_stays}"

    prompt_messages = [SystemMessage(content=system_prompt)] + \
                      state.get("messages", [])

    try:
        response = get_model(model_name).invoke(prompt_messages)
    except LLM_ERRORS:
        logger.exception("Échec de la rédaction de la proposition par le modèle '%s'", model_name)
        response = AIMessage(content=build_fallback_proposal(matching_stays))

    return {"messages": [response]}
