from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any, Optional, Union

from pydantic import BaseModel

from kandor.llm.base import BaseLLM


MockHandler = Callable[[dict[str, Any]], Union[dict[str, Any], BaseModel]]


class MockLLM(BaseLLM):
    def __init__(
        self,
        responses: Optional[dict[str, Union[dict[str, Any], BaseModel, MockHandler]]] = None,
    ) -> None:
        self._responses = responses or {}
        self.calls: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def generate_structured(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        self.calls[prompt_name].append(variables)
        payload = self._responses.get(prompt_name)
        if payload is None:
            return schema.model_validate({})

        if callable(payload):
            payload = payload(variables)

        if isinstance(payload, BaseModel):
            if isinstance(payload, schema):
                return payload
            return schema.model_validate(payload.model_dump())

        return schema.model_validate(payload)
