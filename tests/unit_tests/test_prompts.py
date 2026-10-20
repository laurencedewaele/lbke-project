import os

from dotenv import load_dotenv

from tourism_agent.prompts.prompts import system_prompt_dict


def test_system_prompt_exists_for_configured_model():
    load_dotenv()
    model_name = os.environ["MODEL_NAME"]
    assert model_name in system_prompt_dict, (
        f"Aucun system prompt défini pour le modèle '{model_name}'"
    )
    assert system_prompt_dict[model_name].strip()
