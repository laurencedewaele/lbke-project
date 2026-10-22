"""Comportement de l'agent face aux erreurs (sans appel réseau : le modèle est simulé)."""
import json

import httpx
import openai
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime

from tourism_agent.conditions.staytype_condition import staytype_condition
from tourism_agent.config import require_env
from tourism_agent.exceptions import CatalogError, ConfigurationError
from tourism_agent.nodes import analyze_preferences_node as analyze_module
from tourism_agent.nodes import respond_with_proposal_node as proposal_module
from tourism_agent.nodes.filter_matching_stays_node import filter_matching_stays_node
from tourism_agent.prompts.prompts import PREFERENCES_ANALYSIS_PROMPT_DICT, get_system_prompt
from tourism_agent.schemas.context import Context
from tourism_agent.schemas.criteria import CriteriaIdentificationResult, CriterionOpinion, StayType
from tourism_agent.services import filter_matching_stays as service

MODEL_NAME = next(iter(PREFERENCES_ANALYSIS_PROMPT_DICT))
RUNTIME = Runtime(context=Context(model_name=MODEL_NAME))
BEACH_CRITERIA = CriteriaIdentificationResult(
    criteria=[CriterionOpinion(criterion=StayType.BEACH, avis=True)]
)


class FailingModel:
    """Faux modèle de chat dont chaque appel échoue comme une API indisponible."""

    def with_structured_output(self, schema):
        return self

    def invoke(self, messages):
        raise openai.APIConnectionError(request=httpx.Request("POST", "https://openrouter.ai"))


@pytest.fixture
def failing_model(monkeypatch):
    for module in (analyze_module, proposal_module):
        monkeypatch.setattr(module, "get_model", lambda model_name: FailingModel())


def test_require_env_missing(monkeypatch) -> None:
    monkeypatch.delenv("TOURISM_AGENT_MISSING_VAR", raising=False)
    with pytest.raises(ConfigurationError, match="TOURISM_AGENT_MISSING_VAR"):
        require_env("TOURISM_AGENT_MISSING_VAR")


def test_get_system_prompt_unknown_model() -> None:
    with pytest.raises(ConfigurationError, match="modele-inconnu"):
        get_system_prompt(PREFERENCES_ANALYSIS_PROMPT_DICT, "modele-inconnu")


def test_condition_without_criteria() -> None:
    assert staytype_condition({"messages": []}) == "need_details"


def test_load_catalog_missing_file(tmp_path) -> None:
    with pytest.raises(CatalogError):
        service.load_catalog(tmp_path / "absent.json")


def test_load_catalog_invalid_json(tmp_path) -> None:
    path = tmp_path / "data.json"
    path.write_text("{ pas du json", encoding="utf-8")
    with pytest.raises(CatalogError):
        service.load_catalog(path)


def test_load_catalog_skips_malformed_entries(tmp_path) -> None:
    path = tmp_path / "data.json"
    path.write_text(json.dumps([{"nom": "Séjour valide", "labels": None}, {"labels": ["plage"]}, "x"]),
                    encoding="utf-8")
    assert service.load_catalog(path) == [{"nom": "Séjour valide", "labels": None}]


def test_filter_node_with_unavailable_catalog(monkeypatch) -> None:
    def broken_catalog():
        raise CatalogError("catalogue indisponible")

    monkeypatch.setattr(service, "load_catalog", broken_catalog)
    assert filter_matching_stays_node({"messages": [], "criteria": BEACH_CRITERIA}) == {"matching_stays": []}


def test_analyze_without_messages() -> None:
    assert analyze_module.analyze_preferences_node({"messages": []}, RUNTIME) == {}


def test_analyze_llm_failure_without_previous_criteria(failing_model) -> None:
    state = {"messages": [HumanMessage(content="Je veux aller à la plage")]}
    result = analyze_module.analyze_preferences_node(state, RUNTIME)
    assert result == {"criteria": CriteriaIdentificationResult()}


def test_analyze_llm_failure_keeps_previous_criteria(failing_model) -> None:
    state = {"messages": [HumanMessage(content="Et accessible en fauteuil")], "criteria": BEACH_CRITERIA}
    assert analyze_module.analyze_preferences_node(state, RUNTIME) == {}


def test_proposal_llm_failure_lists_matching_stays(failing_model) -> None:
    state = {
        "messages": [HumanMessage(content="Je veux aller à la plage")],
        "criteria": BEACH_CRITERIA,
        "matching_stays": [{"nom": "Palavas de paillotes en paillotes", "match": "parfait", "score": "1/1"}],
    }
    [message] = proposal_module.respond_with_proposal_node(state, RUNTIME)["messages"]
    assert isinstance(message, AIMessage)
    assert "Palavas de paillotes en paillotes" in message.content
