from ..models.models import State

def staytype_condition(state: State) -> str:
    # Utilise la propriété details_identified pour l'aiguillage
    if state["criteria"].details_identified:
        return "respond_with_confirmation"
    else:
        return "ask_for_details"