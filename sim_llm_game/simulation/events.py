from __future__ import annotations

from sim_llm_game.core.models import Event


class EventFactory:
    @staticmethod
    def create(
        *,
        event_id: str,
        event_type: str,
        timestamp: int,
        participants: list[str] | None = None,
        effects: list[dict] | None = None,
        summary: str = "",
        metadata: dict | None = None,
    ) -> Event:
        return Event(
            id=event_id,
            type=event_type,
            timestamp=timestamp,
            participants=participants or [],
            effects=effects or [],
            summary=summary,
            metadata=metadata or {},
        )
