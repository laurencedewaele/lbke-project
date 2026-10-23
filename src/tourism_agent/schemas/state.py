from langgraph.graph import MessagesState
from typing import NotRequired

from .criteria import CriteriaIdentificationResult


class State(MessagesState):
    # Contient messages par héritage
    criteria: NotRequired[CriteriaIdentificationResult]
    # Séjours du catalogue correspondant aux critères, calculés par filter_matching_stays
    matching_stays: NotRequired[list[dict]]
