from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import request

from pydantic import BaseModel

from sim_llm_game.llm.base import BaseLLM
from sim_llm_game.llm.env import load_dotenv_if_present


@dataclass
class OpenAICompatibleConfig:
    api_key: str
    model: str
    base_url: str = "https://api.openai.com/v1"
    app_name: str = "sim-llm-game"


class OpenAICompatibleLLM(BaseLLM):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        system_prompt: str | None = None,
    ) -> None:
        load_dotenv_if_present(__file__)
        self.config = OpenAICompatibleConfig(
            api_key=api_key or os.environ["OPENAI_API_KEY"],
            model=model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            base_url=(base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/"),
        )
        self.system_prompt = system_prompt or (
            "Return valid JSON that exactly matches the requested schema. "
            "Do not wrap the JSON in markdown fences."
        )

    def generate_structured(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "prompt_name": prompt_name,
                            "variables": variables,
                            "schema": schema.model_json_schema(),
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                },
            },
        }
        req = request.Request(
            f"{self.config.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        return schema.model_validate_json(content)
