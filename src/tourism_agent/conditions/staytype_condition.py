from typing import Literal
from ..models.models import State

def staytype_condition(state: State) -> Literal["detected criteria", "need_details"]:
    # Utilise la propriété details_identified pour l'aiguillage
    if state["criteria"].details_identified:
        return "detected criteria"
    else:
        return "need_details"