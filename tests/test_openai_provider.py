from pydantic import BaseModel

from sim_llm_game.llm.openai import OpenAICompatibleLLM


class DummySchema(BaseModel):
    value: str


def test_openai_provider_uses_env_defaults(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    llm = OpenAICompatibleLLM()
    assert llm.config.api_key == "test-key"
    assert llm.config.model == "gpt-test"
    assert DummySchema.model_json_schema()["type"] == "object"
