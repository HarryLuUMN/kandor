from __future__ import annotations

from sim_llm_game.core.exceptions import ValidationError
from sim_llm_game.core.models import Event
from sim_llm_game.memory.temporal_kg import TemporalKGMemory


def validate_event(event: Event, memory: TemporalKGMemory) -> None:
    for effect in event.effects:
        action = effect.get("action")
        if action not in {"add_relation", "close_relation"}:
            raise ValidationError(f"Unsupported event action: {action}")

        if action == "add_relation":
            required = {"subject", "predicate", "object"}
            missing = required - effect.keys()
            if missing:
                raise ValidationError(
                    f"Missing fields for add_relation effect: {sorted(missing)}"
                )

        if action == "close_relation":
            required = {"subject", "predicate", "object"}
            missing = required - effect.keys()
            if missing:
                raise ValidationError(
                    f"Missing fields for close_relation effect: {sorted(missing)}"
                )

    _validate_no_duplicate_relation_effects(event)
    _validate_close_targets_exist(event, memory)


def _validate_no_duplicate_relation_effects(event: Event) -> None:
    add_effects = set()
    for effect in event.effects:
        if effect.get("action") != "add_relation":
            continue
        key = (effect["subject"], effect["predicate"], effect["object"])
        if key in add_effects:
            raise ValidationError("Event contains duplicate add_relation effects")
        add_effects.add(key)


def _validate_close_targets_exist(event: Event, memory: TemporalKGMemory) -> None:
    open_relations = {
        (relation.subject, relation.predicate, relation.object)
        for relation in memory.relations
        if relation.end_time is None
    }
    for effect in event.effects:
        if effect.get("action") != "close_relation":
            continue
        key = (effect["subject"], effect["predicate"], effect["object"])
        if key not in open_relations:
            raise ValidationError(
                "close_relation effect must target an active open relation"
            )
