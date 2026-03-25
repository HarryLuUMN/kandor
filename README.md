# Kandor

**Kandor** is a Python library for simulated fictional worlds with temporal knowledge graph memory.

_A bottle-city engine for worldbuilding, simulation, and temporal memory._

## V1 Demo Features

- `GodAgent` compiles a user prompt into a structured world blueprint
- `TemporalKGMemory` stores relations and events over time
- `SimulationRunner` advances the world through event application
- `LoreGenerator` turns structured memory into readable summaries
- `MockLLM` makes the full pipeline testable without external model calls
- `OpenAICompatibleLLM` lets the same pipeline run against an OpenAI-compatible chat API
- `TemporalKGWidget` renders saved KG snapshots inside notebooks

## Install

```bash
python3 -m pip install -e '.[dev]'
```

Optional extras:

```bash
python3 -m pip install -e '.[dev,widgets]'
```

## Run The Demo

```bash
python3 examples/demo.py
```

## Docs

A lightweight static documentation site lives under `docs/` and is deployed through GitHub Pages.

- `docs/index.html`
- `docs/getting-started.html`
- `docs/architecture.html`
- `docs/api.html`

## Real LLM smoke test

If you have an OpenAI-compatible API key configured locally, you can run:

```bash
PYTHONPATH=. python3 examples/smoke_openai.py
```

Expected environment variables:
- `OPENAI_API_KEY`
- optional: `OPENAI_MODEL`
- optional: `OPENAI_BASE_URL`

Example provider usage:

```python
from sim_llm_game.builders.world_builder import WorldBuilder
from sim_llm_game.llm.openai import OpenAICompatibleLLM

llm = OpenAICompatibleLLM()
builder = WorldBuilder(llm=llm)
blueprint = builder.create_world(
    prompt="Create a world of fractured moon colonies linked by ritual trade."
)
```

## Temporal KG widget

A notebook widget can visualize a temporal KG snapshot with `anywidget` and `d3.js`.

Install optional widget dependencies:

```bash
python3 -m pip install -e '.[widgets]'
```

Then in a notebook:

```python
from sim_llm_game import TemporalKGWidget
widget = TemporalKGWidget('reports/smoke/openai-smoke-kg-2026-03-24.json')
widget
```

You can also load the snapshot data directly:

```python
from sim_llm_game import load_temporal_kg_snapshot

data = load_temporal_kg_snapshot("reports/smoke/openai-smoke-kg-2026-03-24.json")
```

## Minimal Usage

```python
from sim_llm_game import LoreGenerator, SimulationRunner, WorldBuilder
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
memory = builder.create_memory(blueprint)
runner = SimulationRunner(world=blueprint.spec, memory=memory)
lore = LoreGenerator(llm=llm)
```
