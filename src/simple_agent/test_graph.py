"""Minimal LangChain agent graph for deployment."""

from __future__ import annotations
from typing import TypedDict

import os
from datetime import datetime, timezone

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import Runtime
from langchain.chat_models import init_chat_model
from langchain.tools import ToolRuntime
from langchain_core.tools import tool

# For OpenRouter, we won't use this default setup at all
# DEFAULT_MODEL = os.getenv("SIMPLE_AGENT_MODEL", "anthropic:claude-sonnet-4-6")

# https://openrouter.ai/docs/guides/community/langchain
model = init_chat_model(
    model="gemini-3.5-flash-lite",
    model_provider="openai",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from typing import Literal

class State(TypedDict):
    input: str
    output: str

# Guardrail
def is_about_langchain(state: State)-> Literal["RELEVANT", "IRRELEVANT"]:
  if state["input"].find("langchain") > -1:
    return "RELEVANT"
  else:
    return "IRRELEVANT"

def call_model(state: State):
  prompt=f"""{state["input"]}"""
  return {
      "output": model.invoke(prompt).content
  }

router_builder = StateGraph(
    state_schema=State
)
router_builder.add_node("call_model_node", call_model)
router_builder.add_conditional_edges(
                                    # start node
                                      START,
                                     # condition
                                     is_about_langchain,
                                     # Possible end nodes
                                      {"RELEVANT": "call_model_node", "IRRELEVANT": END},)
# Alternative syntax : add type to the edge function: ->Literal["call_model", "__end__"]:

graph = router_builder.compile()