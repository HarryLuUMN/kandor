from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from sim_llm_game.core.types import EntityType


class WorldSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    premise: str
    genre: str
    rules: list[str] = Field(default_factory=list)
    ontology: dict[str, list[str]] = Field(default_factory=dict)
    simulation_parameters: dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: EntityType
    name: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class Relation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str
    predicate: str
    object: str
    start_time: int
    end_time: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_time_range(self) -> "Relation":
        if self.end_time is not None and self.end_time < self.start_time:
            raise ValueError("end_time must be greater than or equal to start_time")
        return self

    def is_active_at(self, time: int) -> bool:
        if time < self.start_time:
            return False
        if self.end_time is None:
            return True
        return time <= self.end_time

    def overlaps(self, start_time: int, end_time: int | None) -> bool:
        left_end = self.end_time if self.end_time is not None else float("inf")
        right_end = end_time if end_time is not None else float("inf")
        return self.start_time <= right_end and start_time <= left_end


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: str
    timestamp: int
    participants: list[str] = Field(default_factory=list)
    effects: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
