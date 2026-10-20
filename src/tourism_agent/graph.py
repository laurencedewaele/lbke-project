"""Graphe de l'agent de tourisme : assemblage uniquement (nœuds et conditions sont dans leurs modules)."""

from langgraph.graph import StateGraph, START, END

from .models.models import State
from .nodes.analyze_preferences_node import analyze_preferences_node
from .nodes.respond_with_confirmation_node import respond_with_confirmation_node
from .nodes.ask_for_details_node import ask_for_details_node
from .conditions.staytype_condition import staytype_condition


# Construction du graphe
workflow = StateGraph(State)
workflow.add_node("analyze_preferences", analyze_preferences_node)
workflow.add_node("respond_with_confirmation", respond_with_confirmation_node)
workflow.add_node("ask_for_details", ask_for_details_node)

workflow.add_edge(START, "analyze_preferences")
workflow.add_conditional_edges(
    "analyze_preferences",
    staytype_condition,
    {
        "respond_with_confirmation": "respond_with_confirmation",
        "ask_for_details": "ask_for_details"
    }
)
workflow.add_edge("respond_with_confirmation", END)
workflow.add_edge("ask_for_details", END)

graph = workflow.compile()
