from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Optional

from kandor.core.models import Event, WorldSpec, WorldState
from kandor.memory.retrieval import RelevantContext
from kandor.memory.temporal_kg import TemporalKGMemory
from kandor.simulation.rules import validate_event
from kandor.simulation.updater import WorldUpdater


EventSelector = Callable[[RelevantContext, Sequence[Event]], Optional[Event]]


class SimulationRunner:
    def __init__(
        self,
        *,
        world: WorldSpec,
        memory: TemporalKGMemory | None = None,
        state: WorldState | None = None,
        selector: EventSelector | None = None,
        updater: WorldUpdater | None = None,
    ) -> None:
        self.world = world
        self.memory = memory or TemporalKGMemory()
        self.state = state or WorldState()
        self.selector = selector or self._default_selector
        self.updater = updater or WorldUpdater()

    def step(self, candidate_events: Sequence[Event]) -> Event | None:
        context = self.memory.get_relevant_context(
            entity_ids=self.state.entity_ids,
            time=self.state.current_time,
            horizon=1,
        )
        selected_event = self.selector(context, candidate_events)
        if selected_event is None:
            self.state.current_time += 1
            return None

        validate_event(selected_event, self.memory)
        self.updater.apply(
            event=selected_event,
            memory=self.memory,
            state=self.state,
        )
        return selected_event

    @staticmethod
    def _default_selector(
        _context: RelevantContext, candidate_events: Sequence[Event]
    ) -> Optional[Event]:
        if not candidate_events:
            return None
        return sorted(candidate_events, key=lambda event: (event.timestamp, event.id))[0]
