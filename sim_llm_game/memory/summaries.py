from __future__ import annotations

from sim_llm_game.core.models import Event, Relation


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
