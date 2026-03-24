from sim_llm_game import LoreGenerator, SimulationRunner, WorldBuilder
from sim_llm_game.core.models import Event
from sim_llm_game.llm.mock import MockLLM


def main() -> None:
    llm = MockLLM(
        responses={
            "god_agent": {
                "premise": "A tidal world of rival ports and failing relic engines.",
                "genre": "science_fantasy",
                "rules": ["Relic engines reshape tides but consume rare fuel."],
                "ontology": {
                    "entity_types": ["faction", "location", "artifact"],
                    "relation_types": ["controls", "trades_with", "allied_with"],
                },
                "simulation_parameters": {"tick_unit": "season"},
                "entities": [
                    {
                        "id": "faction.tide_court",
                        "type": "faction",
                        "name": "The Tide Court",
                    },
                    {
                        "id": "location.lantern_port",
                        "type": "location",
                        "name": "Lantern Port",
                    },
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
                        "id": "event.fuel_shortage",
                        "type": "resource_shortage",
                        "timestamp": 0,
                        "participants": ["faction.tide_court"],
                        "summary": "The Tide Court faces a relic fuel shortage.",
                    }
                ],
            },
            "lore_summary": lambda variables: {
                "summary": (
                    f"At time {variables['time']}, the world state is: "
                    f"{variables['world_state']}. Recent developments: {variables['relevant_events']}."
                )
            },
        }
    )

    builder = WorldBuilder(llm=llm)
    blueprint = builder.create_world(
        prompt="Make a maritime science-fantasy setting with ancient engines and tense port politics."
    )
    memory = builder.create_memory(blueprint)
    runner = SimulationRunner(world=blueprint.spec, memory=memory)

    runner.step(
        [
            Event(
                id="event.alliance",
                type="alliance_formed",
                timestamp=1,
                participants=["faction.tide_court", "faction.harbor_union"],
                effects=[
                    {
                        "action": "add_relation",
                        "subject": "faction.tide_court",
                        "predicate": "allied_with",
                        "object": "faction.harbor_union",
                    }
                ],
                summary="The Tide Court signs a pact with the Harbor Union.",
            )
        ]
    )

    lore = LoreGenerator(llm=llm)
    print(lore.summarize_world(memory=runner.memory, time=runner.state.current_time))


if __name__ == "__main__":
    main()
