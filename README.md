# sim-llm-game

`sim-llm-game` is a Python library for LLM-based world building backed by temporal knowledge graph memory.

## V1 Demo Features

- `GodAgent` compiles a user prompt into a structured world blueprint
- `TemporalKGMemory` stores relations and events over time
- `SimulationRunner` advances the world through event application
- `LoreGenerator` turns structured memory into readable summaries
- `MockLLM` makes the full pipeline testable without external model calls

## Install

```bash
python3 -m pip install -e '.[dev]'
```

## Run The Demo

```bash
python3 examples/demo.py
```

## Docs

A lightweight static documentation site lives under `docs/` and is deployed through GitHub Pages.

## Real LLM smoke test

If you have an OpenAI-compatible API key configured locally, you can run:

```bash
PYTHONPATH=. python3 examples/smoke_openai.py
```

Expected environment variables:
- `OPENAI_API_KEY`
- optional: `OPENAI_MODEL`
- optional: `OPENAI_BASE_URL`

## Minimal Usage

```python
from sim_llm_game import SimulationRunner, WorldBuilder
from sim_llm_game.llm.mock import MockLLM

llm = MockLLM(
    responses={
        "god_agent": {
            "premise": "A broken empire of sandglass cities.",
            "genre": "fantasy",
        }
    }
)

builder = WorldBuilder(llm=llm)
blueprint = builder.create_world(prompt="Make a desert empire with unstable time magic.")
runner = SimulationRunner(world=blueprint.spec, memory=builder.create_memory(blueprint))
```
