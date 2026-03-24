from __future__ import annotations

from collections import defaultdict

from sim_llm_game.core.exceptions import MemoryConflictError
from sim_llm_game.core.models import Event, Relation
from sim_llm_game.memory.retrieval import EntityHistory, RelevantContext


class TemporalKGMemory:
    def __init__(self) -> None:
        self._relations: list[Relation] = []
        self._events: list[Event] = []
        self._relation_index: dict[str, list[Relation]] = defaultdict(list)

    @property
    def relations(self) -> list[Relation]:
        return list(self._relations)

    @property
    def events(self) -> list[Event]:
        return list(self._events)

    def add_relation(self, relation: Relation) -> Relation:
        for existing in self._relation_index[relation.subject]:
            if (
                existing.predicate == relation.predicate
                and existing.object == relation.object
                and existing.overlaps(relation.start_time, relation.end_time)
            ):
                raise MemoryConflictError(
                    "Overlapping relation already exists for subject/predicate/object"
                )
        self._relations.append(relation)
        self._relation_index[relation.subject].append(relation)
        return relation

    def close_relation(
        self,
        *,
        subject: str,
        predicate: str,
        object: str,
        end_time: int,
    ) -> Relation:
        candidates = [
            relation
            for relation in self._relation_index.get(subject, [])
            if relation.predicate == predicate
            and relation.object == object
            and relation.end_time is None
        ]
        if not candidates:
            raise MemoryConflictError("No open relation found to close")
        relation = max(candidates, key=lambda item: item.start_time)
        if end_time < relation.start_time:
            raise MemoryConflictError("Cannot close relation before its start time")
        relation.end_time = end_time
        return relation

    def add_event(self, event: Event) -> Event:
        self._events.append(event)
        self._events.sort(key=lambda item: item.timestamp)
        return event

    def get_world_state_at(self, time: int) -> list[Relation]:
        return [
            relation for relation in self._relations if relation.is_active_at(time)
        ]

    def get_entity_history(self, entity_id: str) -> EntityHistory:
        relations = [
            relation
            for relation in self._relations
            if relation.subject == entity_id or relation.object == entity_id
        ]
        events = [
            event for event in self._events if entity_id in event.participants
        ]
        relations.sort(key=lambda item: (item.start_time, item.predicate, item.object))
        events.sort(key=lambda item: (item.timestamp, item.id))
        return EntityHistory(entity_id=entity_id, relations=relations, events=events)

    def get_active_relations(
        self, entity_id: str, time: int | None = None
    ) -> list[Relation]:
        relations = [
            relation
            for relation in self._relations
            if relation.subject == entity_id or relation.object == entity_id
        ]
        if time is None:
            return relations
        return [relation for relation in relations if relation.is_active_at(time)]

    def get_events_between(self, start: int, end: int) -> list[Event]:
        return [event for event in self._events if start <= event.timestamp <= end]

    def get_relevant_context(
        self, entity_ids: list[str], time: int, horizon: int
    ) -> RelevantContext:
        relation_set: list[Relation] = []
        seen_relations: set[tuple[str, str, str, int, int | None]] = set()
        for entity_id in entity_ids:
            for relation in self.get_active_relations(entity_id, time=time):
                key = (
                    relation.subject,
                    relation.predicate,
                    relation.object,
                    relation.start_time,
                    relation.end_time,
                )
                if key in seen_relations:
                    continue
                seen_relations.add(key)
                relation_set.append(relation)

        start = max(0, time - horizon)
        end = time + horizon
        events = [
            event
            for event in self.get_events_between(start, end)
            if not entity_ids or any(participant in entity_ids for participant in event.participants)
        ]
        return RelevantContext(
            entity_ids=entity_ids,
            time=time,
            horizon=horizon,
            relations=sorted(
                relation_set,
                key=lambda item: (item.start_time, item.subject, item.predicate, item.object),
            ),
            events=events,
        )
