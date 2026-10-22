from langgraph.graph import MessagesState
from typing import NotRequired

from .criteria import CriteriaIdentificationResult


class State(MessagesState):
    # Contient messages par héritage
    # Absent tant que analyze_preferences n'a pas tourné (pas de valeur par défaut dans un TypedDict)
    criteria: NotRequired[CriteriaIdentificationResult]

    # Séjours du catalogue correspondant aux critères, calculés par filter_matching_stays
    matching_stays: NotRequired[list[dict]]
