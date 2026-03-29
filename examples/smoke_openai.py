from kandor import LoreGenerator, SimulationRunner, WorldBuilder
from kandor.core.models import Event
from kandor.llm.openai import OpenAICompatibleLLM


def main() -> None:
    llm = OpenAICompatibleLLM()
    builder = WorldBuilder(llm=llm)
    blueprint = builder.create_world(
        prompt="Create a compact fantasy world with 2 factions, 2 locations, one tension, and one seed event."
    )
    memory = builder.create_memory(blueprint)
    runner = SimulationRunner(world=blueprint.spec, memory=memory)

    candidate = Event(
        id="event.smoke.step1",
        type="alliance_formed",
        timestamp=1,
        participants=[entity.id for entity in blueprint.entities[:2]],
        effects=[],
        summary="A tentative alliance forms during the smoke test.",
    )
    runner.step([candidate])

    lore = LoreGenerator(llm=llm)
    summary = lore.summarize_world(memory=runner.memory, time=runner.state.current_time)

    print("SMOKE_TEST_OK")
    print("premise:", blueprint.spec.premise)
    print("genre:", blueprint.spec.genre)
    print("entities:", len(blueprint.entities))
    print("relations:", len(memory.relations))
    print("events:", len(memory.events))
    print("time:", runner.state.current_time)
    print("summary:", summary)


if __name__ == "__main__":
    main()
