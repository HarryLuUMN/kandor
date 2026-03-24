from sim_llm_game.generation.lore import LoreGenerator
from sim_llm_game.llm.mock import MockLLM
from sim_llm_game.core.models import Event, Relation
from sim_llm_game.memory.summaries import summarize_world_state
from sim_llm_game.memory.temporal_kg import TemporalKGMemory


def test_lore_generator_summarizes_world() -> None:
    llm = MockLLM(
        responses={
            "lore_summary": lambda variables: {
                "summary": f"Summary at {variables['time']}: {variables['world_state']}"
            }
        }
    )
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="faction.tide_court",
            predicate="controls",
            object="location.lantern_port",
            start_time=0,
        )
    )

    generator = LoreGenerator(llm=llm)
    summary = generator.summarize_world(memory=memory, time=0)

    assert "faction.tide_court controls location.lantern_port" in summary


def test_summarize_world_state_uses_relations_and_events() -> None:
    memory = TemporalKGMemory()
    memory.add_relation(
        Relation(
            subject="city.alpha",
            predicate="trades_with",
            object="city.beta",
            start_time=1,
        )
    )
    memory.add_event(
        Event(
            id="event.1",
            type="trade_pact",
            timestamp=1,
            participants=["city.alpha", "city.beta"],
            summary="Alpha and Beta sign a trade pact.",
        )
    )

    summary = summarize_world_state(memory, time=1)

    assert "Relations:" in summary
    assert "Recent events:" in summary
