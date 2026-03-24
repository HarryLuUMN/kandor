from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from sim_llm_game.llm.base import BaseLLM
from sim_llm_game.memory.summaries import summarize_events, summarize_relations
from sim_llm_game.memory.temporal_kg import TemporalKGMemory


class LoreSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str


class LoreGenerator:
    def __init__(self, *, llm: BaseLLM) -> None:
        self.llm = llm

    def summarize_world(self, *, memory: TemporalKGMemory, time: int) -> str:
        relations = memory.get_world_state_at(time)
        events = memory.get_events_between(max(0, time - 3), time)
        result = self.llm.generate_structured(
            prompt_name="lore_summary",
            variables={
                "world_state": summarize_relations(relations),
                "entity_history": "",
                "relevant_events": summarize_events(events),
                "time": time,
            },
            schema=LoreSummary,
        )
        return result.summary

    def summarize_entity(
        self, *, memory: TemporalKGMemory, entity_id: str, time: int
    ) -> str:
        history = memory.get_entity_history(entity_id)
        active_relations = memory.get_active_relations(entity_id, time=time)
        result = self.llm.generate_structured(
            prompt_name="lore_summary",
            variables={
                "world_state": summarize_relations(active_relations),
                "entity_history": summarize_events(history.events),
                "relevant_events": summarize_events(
                    [event for event in history.events if event.timestamp <= time]
                ),
                "time": time,
                "entity_id": entity_id,
            },
            schema=LoreSummary,
        )
        return result.summary
