from ..models.models import State, CriteriaIdentificationResult
import os
from ..prompts.prompts import system_prompt_dict
from ..llm import model
from langchain_core.messages import SystemMessage, HumanMessage

# Récupération du prompt système pour le modèle spécifié
# L'existence d'un prompt système pour le modèle spécifié aura été vérifiée lors des tests.
system_prompt = system_prompt_dict.get(os.environ["MODEL_NAME"], "")

# Définition d'une fonction d'analyse de préférences qui fusionne/enrichit l'état existant
def analyze_preferences_node(state: State) -> dict:
    # On analyse uniquement le dernier message reçu de l'utilisateur
    user_message = state["messages"][-1].content

    model_with_output = model.with_structured_output(CriteriaIdentificationResult)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Client: {user_message}")
    ]
    nouveaux_criteres = model_with_output.invoke(messages)

    # Récupération des anciens critères stockés dans l'état (si existants)
    criteres_existants = state.get("criteria")

    if criteres_existants is None or not criteres_existants.criteria:
        # S'il n'y avait rien, on prend la nouvelle analyse brute
        criteres_finaux = nouveaux_criteres
    else:
        # Sinon, on procède à la fusion (merging)
        criteres_dict = {c.criterion: c for c in criteres_existants.criteria}

        if nouveaux_criteres.criteria:
            for nouv in nouveaux_criteres.criteria:
                # On ajoute ou met à jour le critère spécifique
                criteres_dict[nouv.criterion] = nouv

        # Reconstruction de la liste finale pour le Pydantic Model
        criteres_finaux = CriteriaIdentificationResult(criteria=list(criteres_dict.values()))

    return {
        "criteria": criteres_finaux,
        "request": user_message
    }