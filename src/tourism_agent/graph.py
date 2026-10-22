"""Graphe de l'agent de tourisme : assemblage uniquement (nœuds et conditions sont dans leurs modules)."""
from langgraph.graph import StateGraph, START, END

from .schemas.context import Context
from .schemas.state import State
from .nodes.analyze_preferences_node import analyze_preferences_node
from .nodes.filter_matching_stays_node import filter_matching_stays_node
from .nodes.respond_with_proposal_node import respond_with_proposal_node
from .nodes.ask_for_details_node import ask_for_details_node
from .conditions.staytype_condition import staytype_condition


# Construction du graphe
workflow = StateGraph(State, context_schema=Context)

workflow.add_node("analyze_preferences", analyze_preferences_node)
workflow.add_node("filter_matching_stays", filter_matching_stays_node)
workflow.add_node("respond_with_proposal", respond_with_proposal_node)
workflow.add_node("ask_for_details", ask_for_details_node)

# Définition des transitions
workflow.add_edge(START, "analyze_preferences")
workflow.add_conditional_edges(
    "analyze_preferences",
    staytype_condition,
    {
        "criteria_detected": "filter_matching_stays",
        "need_details": "ask_for_details"
    }
)

workflow.add_edge("filter_matching_stays", "respond_with_proposal")
workflow.add_edge("respond_with_proposal", END)
workflow.add_edge("ask_for_details", END)

graph = workflow.compile()