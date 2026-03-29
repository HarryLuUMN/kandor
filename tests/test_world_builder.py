from kandor import WorldBuilder
from kandor.llm.mock import MockLLM


def test_world_builder_creates_structured_blueprint() -> None:
    llm = MockLLM(
        responses={
            "god_agent": {
                "premise": "A storm-wracked ocean world with city-states and relic engines.",
                "genre": "science_fantasy",
                "rules": ["Relic engines can alter tides but require rare fuel."],
                "ontology": {
                    "entity_types": ["faction", "location", "artifact"],
                    "relation_types": ["controls", "trades_with"],
                },
                "simulation_parameters": {"tick_unit": "season"},
                "entities": [
                    {
                        "id": "faction.tide_court",
                        "type": "faction",
                        "name": "The Tide Court",
                    }
                ],
                "relations": [
                    {
                        "subject": "faction.tide_court",
                        "predicate": "controls",
                        "object": "location.lantern_port",
                        "start_time": 0,
                    }
                ],
                "seed_events": [
                    {
                        "id": "event.relic_shortage",
                        "type": "resource_shortage",
                        "timestamp": 0,
                        "participants": ["faction.tide_court"],
                        "summary": "Fuel for the relic engines is running low.",
                    }
                ],
            }
        }
    )
    builder = WorldBuilder(llm=llm)

    blueprint = builder.create_world(
        prompt="Make a maritime world with old machine relics and rival port cities."
    )

    assert blueprint.spec.genre == "science_fantasy"
    assert blueprint.entities[0].id == "faction.tide_court"
    assert blueprint.relations[0].object == "location.lantern_port"
    assert blueprint.seed_events[0].id == "event.relic_shortage"


def test_world_builder_can_seed_memory_from_blueprint() -> None:
    llm = MockLLM(
        responses={
            "god_agent": {
                "premise": "A fractured desert world.",
                "genre": "fantasy",
                "entities": [],
                "relations": [
                    {
                        "subject": "city.glass",
                        "predicate": "trades_with",
                        "object": "city.salt",
                        "start_time": 0,
                    }
                ],
                "seed_events": [
                    {
                        "id": "event.1",
                        "type": "trade_pact",
                        "timestamp": 0,
                        "participants": ["city.glass", "city.salt"],
                    }
                ],
            }
        }
    )
    builder = WorldBuilder(llm=llm)
    blueprint = builder.create_world(prompt="Make a desert trade world.")

    memory = builder.create_memory(blueprint)

    assert len(memory.relations) == 1
    assert len(memory.events) == 1
