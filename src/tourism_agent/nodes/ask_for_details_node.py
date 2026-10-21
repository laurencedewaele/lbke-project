from ..models.models import State, StayType
from langchain_core.messages import AIMessage

def ask_for_details_node(state: State) -> dict:
    # Récupération des types de séjour disponibles
    formatted_stay_types = "\n".join(f"- {stay_type.value}" for stay_type in StayType)

    # Template statique
    full_response = (
        "Bonjour ! Pour que je puisse vous proposer le séjour idéal, j'ai besoin de quelques précisions sur vos envies.\n"
        "Pourriez-vous m'indiquer vos préférences parmi les choix suivants :\n\n"
        f"{formatted_stay_types}\n"
    )
    return {
        "answer": full_response,
        "messages": [AIMessage(content=full_response)]
    }