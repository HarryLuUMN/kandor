from pydantic import ValidationError

from sim_llm_game.core.models import Relation, WorldSpec


def test_world_spec_defaults_are_valid() -> None:
    spec = WorldSpec(
        premise="A world of drifting islands.",
        genre="fantasy",
    )

    assert spec.rules == []
    assert spec.ontology == {}


def test_relation_rejects_invalid_time_range() -> None:
    try:
        Relation(
            subject="city.alpha",
            predicate="controlled_by",
            object="kingdom.red",
            start_time=5,
            end_time=4,
        )
    except ValidationError:
        assert True
    else:
        assert False, "Expected ValidationError"
