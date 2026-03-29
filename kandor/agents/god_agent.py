from __future__ import annotations

from importlib import resources

import yaml
from pydantic import BaseModel, ConfigDict, Field

from kandor.core.models import Entity, Event, Relation, WorldBlueprint, WorldSpec
from kandor.llm.base import BaseLLM


class GodAgentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    premise: str
    genre: str
    rules: list[str] = Field(default_factory=list)
    ontology: dict[str, list[str]] = Field(default_factory=dict)
    simulation_parameters: dict[str, int | str | float | bool] = Field(default_factory=dict)
    entities: list[Entity] = Field(default_factory=list)
    relations: list[Relation] = Field(default_factory=list)
    seed_events: list[Event] = Field(default_factory=list)


class GodAgent:
    def __init__(self, *, llm: BaseLLM, prompt_name: str = "god_agent") -> None:
        self.llm = llm
        self.prompt_name = prompt_name

    def create_world(self, prompt: str) -> WorldBlueprint:
        prompt_config = self.load_prompt(self.prompt_name)
        result = self.llm.generate_structured(
            prompt_name=self.prompt_name,
            variables={
                "user_prompt": prompt,
                "prompt_config": prompt_config,
            },
            schema=GodAgentOutput,
        )
        spec = WorldSpec(
            premise=result.premise,
            genre=result.genre,
            rules=result.rules,
            ontology=result.ontology,
            simulation_parameters=result.simulation_parameters,
        )
        return WorldBlueprint(
            spec=spec,
            entities=result.entities,
            relations=result.relations,
            seed_events=result.seed_events,
        )

    @staticmethod
    def load_prompt(prompt_name: str) -> dict:
        prompt_resource = resources.files("kandor.prompts").joinpath(f"{prompt_name}.yaml")
        return yaml.safe_load(prompt_resource.read_text(encoding="utf-8"))
