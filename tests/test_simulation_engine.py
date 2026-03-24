import pytest

from sim_llm_game.core.exceptions import ValidationError
from sim_llm_game.core.models import Event, Relation, WorldSpec, WorldState
from sim_llm_game.memory.temporal_kg import TemporalKGMemory
from sim_llm_game.simulation.engine import SimulationRunner


def test_simulation_runner_applies_event_and_updates_memory() -> None:
    world = WorldSpec(premise="A tense archipelago.", genre="fantasy")
    runner = SimulationRunner(world=world, state=WorldState(current_time=1))

    event = Event(
        id="event.1",
        type="alliance_formed",
        timestamp=2,
        participants=["kingdom.red", "guild.embers"],
        effects=[
            {
                "action": "add_relation",
                "subject": "kingdom.red",
                "predicate": "allied_with",
                "object": "guild.embers",
            }
        ],
        summary="Kingdom Red forms an alliance with the Embers guild.",
    )

    selected = runner.step([event])

    assert selected is not None
    assert runner.state.current_time == 2
    assert runner.memory.events[0].id == "event.1"
    assert runner.memory.get_active_relations("kingdom.red", time=2)[0].object == "guild.embers"


def test_simulation_runner_uses_first_sorted_event_by_default() -> None:
    world = WorldSpec(premise="A tense archipelago.", genre="fantasy")
    runner = SimulationRunner(world=world)

    later = Event(
        id="event.2",
        type="festival",
        timestamp=3,
    )
    earlier = Event(
        id="event.1",
        type="battle",
        timestamp=2,
    )

    selected = runner.step([later, earlier])

    assert selected is not None
    assert selected.id == "event.1"


def test_simulation_runner_advances_time_when_no_event_selected() -> None:
    world = WorldSpec(premise="A tense archipelago.", genre="fantasy")
    runner = SimulationRunner(world=world, state=WorldState(current_time=4))

    selected = runner.step([])

    assert selected is None
    assert runner.state.current_time == 5


def test_simulation_runner_rejects_invalid_close_effect() -> None:
    world = WorldSpec(premise="A tense archipelago.", genre="fantasy")
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="kingdom.red",
            predicate="allied_with",
            object="guild.embers",
            start_time=1,
            end_time=2,
        )
    )
    runner = SimulationRunner(world=world, memory=memory)

    event = Event(
        id="event.3",
        type="alliance_broken",
        timestamp=3,
        effects=[
            {
                "action": "close_relation",
                "subject": "kingdom.red",
                "predicate": "allied_with",
                "object": "guild.embers",
            }
        ],
    )

    with pytest.raises(ValidationError):
        runner.step([event])
