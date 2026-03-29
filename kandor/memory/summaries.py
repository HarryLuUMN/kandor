from __future__ import annotations

from kandor.core.models import Event, Relation
from kandor.memory.temporal_kg import TemporalKGMemory


def summarize_relations(relations: list[Relation]) -> str:
    if not relations:
        return "No active relations."
    return "; ".join(
        f"{relation.subject} {relation.predicate} {relation.object}"
        for relation in relations
    )


def summarize_events(events: list[Event]) -> str:
    if not events:
        return "No recorded events."
    return "; ".join(event.summary or event.id for event in events)


def summarize_world_state(memory: TemporalKGMemory, time: int) -> str:
    relations = memory.get_world_state_at(time)
    events = memory.get_events_between(max(0, time - 3), time)
    return "\n".join(
        [
            f"Time: {time}",
            f"Relations: {summarize_relations(relations)}",
            f"Recent events: {summarize_events(events)}",
        ]
    )
