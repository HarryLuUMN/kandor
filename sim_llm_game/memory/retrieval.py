from __future__ import annotations

from dataclasses import dataclass

from sim_llm_game.core.models import Event, Relation


@dataclass(slots=True)
class RelevantContext:
    entity_ids: list[str]
    time: int
    horizon: int
    relations: list[Relation]
    events: list[Event]


@dataclass(slots=True)
class EntityHistory:
    entity_id: str
    relations: list[Relation]
    events: list[Event]
