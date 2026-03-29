from kandor.core.exceptions import MemoryConflictError
from kandor.core.models import Event, Relation
from kandor.memory.temporal_kg import TemporalKGMemory


def test_add_relation_and_query_world_state() -> None:
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="city.alpha",
            predicate="controlled_by",
            object="kingdom.red",
            start_time=1,
            end_time=3,
        )
    )
    memory.add_relation(
        Relation(
            subject="city.alpha",
            predicate="controlled_by",
            object="kingdom.blue",
            start_time=4,
        )
    )

    state = memory.get_world_state_at(2)

    assert len(state) == 1
    assert state[0].object == "kingdom.red"


def test_close_relation_marks_interval_end() -> None:
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="guild.embers",
            predicate="allied_with",
            object="kingdom.red",
            start_time=2,
        )
    )

    closed = memory.close_relation(
        subject="guild.embers",
        predicate="allied_with",
        object="kingdom.red",
        end_time=5,
    )

    assert closed.end_time == 5
    assert memory.get_active_relations("guild.embers", time=6) == []


def test_overlapping_relation_raises_conflict() -> None:
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="city.alpha",
            predicate="controlled_by",
            object="kingdom.red",
            start_time=1,
            end_time=4,
        )
    )

    try:
        memory.add_relation(
            Relation(
                subject="city.alpha",
                predicate="controlled_by",
                object="kingdom.red",
                start_time=3,
                end_time=5,
            )
        )
    except MemoryConflictError:
        assert True
    else:
        assert False, "Expected MemoryConflictError"


def test_get_entity_history_includes_relations_and_events() -> None:
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="kingdom.red",
            predicate="rules",
            object="city.alpha",
            start_time=1,
        )
    )
    memory.add_event(
        Event(
            id="event.1",
            type="battle",
            timestamp=2,
            participants=["kingdom.red", "city.alpha"],
            summary="A battle at Alpha.",
        )
    )

    history = memory.get_entity_history("kingdom.red")

    assert len(history.relations) == 1
    assert len(history.events) == 1


def test_get_relevant_context_filters_by_time_and_entity() -> None:
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="city.alpha",
            predicate="controlled_by",
            object="kingdom.red",
            start_time=1,
        )
    )
    memory.add_event(
        Event(
            id="event.1",
            type="battle",
            timestamp=3,
            participants=["city.alpha"],
            summary="Battle at Alpha.",
        )
    )
    memory.add_event(
        Event(
            id="event.2",
            type="festival",
            timestamp=10,
            participants=["city.beta"],
            summary="Festival at Beta.",
        )
    )

    context = memory.get_relevant_context(["city.alpha"], time=4, horizon=2)

    assert len(context.relations) == 1
    assert len(context.events) == 1
    assert context.events[0].id == "event.1"
