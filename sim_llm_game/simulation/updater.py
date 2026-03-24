from __future__ import annotations

from sim_llm_game.core.models import Event, Relation, WorldState
from sim_llm_game.memory.temporal_kg import TemporalKGMemory


class WorldUpdater:
    def apply(self, *, event: Event, memory: TemporalKGMemory, state: WorldState) -> None:
        for effect in event.effects:
            action = effect["action"]
            if action == "add_relation":
                memory.add_relation(
                    Relation(
                        subject=effect["subject"],
                        predicate=effect["predicate"],
                        object=effect["object"],
                        start_time=event.timestamp,
                        end_time=effect.get("end_time"),
                        metadata=effect.get("metadata", {}),
                    )
                )
            elif action == "close_relation":
                memory.close_relation(
                    subject=effect["subject"],
                    predicate=effect["predicate"],
                    object=effect["object"],
                    end_time=effect.get("end_time", event.timestamp),
                )

        memory.add_event(event)
        state.current_time = event.timestamp
        state.entity_ids = sorted(
            {
                *state.entity_ids,
                *event.participants,
                *[
                    effect[key]
                    for effect in event.effects
                    for key in ("subject", "object")
                    if key in effect
                ],
            }
        )
