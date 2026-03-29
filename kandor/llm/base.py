from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseLLM(ABC):
    @abstractmethod
    def generate_structured(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        raise NotImplementedError
