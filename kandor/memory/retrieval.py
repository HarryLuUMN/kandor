from __future__ import annotations

from dataclasses import dataclass

from kandor.core.models import Event, Relation


@dataclass
class RelevantContext:
    entity_ids: list[str]
    time: int
    horizon: int
    relations: list[Relation]
    events: list[Event]


@dataclass
class EntityHistory:
    entity_id: str
    relations: list[Relation]
    events: list[Event]
