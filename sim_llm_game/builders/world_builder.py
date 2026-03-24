from __future__ import annotations

from sim_llm_game.agents.god_agent import GodAgent
from sim_llm_game.core.models import WorldBlueprint
from sim_llm_game.llm.base import BaseLLM
from sim_llm_game.memory.temporal_kg import TemporalKGMemory


class WorldBuilder:
    def __init__(self, *, llm: BaseLLM) -> None:
        self.llm = llm

    def create_world(self, *, prompt: str) -> WorldBlueprint:
        return GodAgent(llm=self.llm).create_world(prompt)

    def create_memory(self, blueprint: WorldBlueprint) -> TemporalKGMemory:
        memory = TemporalKGMemory()
        for relation in blueprint.relations:
            memory.add_relation(relation)
        for event in blueprint.seed_events:
            memory.add_event(event)
        return memory
