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
python3 -m pip install kandor
```

Optional extras:

```bash
python3 -m pip install 'kandor[widgets]'
```

## Quickstart

```bash
python3 - <<'PY'
from kandor import WorldBuilder
from kandor.llm.mock import MockLLM

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
print(blueprint.spec)
PY
```

## Notebook Examples

Introduction:
Kandor now includes starter Jupyter notebooks for the most common library workflows.

Usage:
These notebooks live in the source repository under `examples/notebooks/`.
- `examples/notebooks/01_quickstart_world_pipeline.ipynb` walks through world creation, simulation, and lore generation
- `examples/notebooks/02_temporal_kg_queries.ipynb` focuses on temporal memory queries and retrieval
- `examples/notebooks/03_temporal_kg_widget.ipynb` shows the notebook widget for saved KG snapshots
- `examples/notebooks/04_openai_world_pipeline.ipynb` runs the same pipeline against a real OpenAI-compatible backend

Current status:
- these notebooks are starter examples for local exploration
- they are designed to run with the current mock pipeline and bundled snapshot data
- the widget notebook requires the optional `widgets` extras
- the OpenAI backend notebook expects `OPENAI_API_KEY` plus optional `OPENAI_MODEL` and `OPENAI_BASE_URL`, which can come from the environment or the repository `.env`
- they are not included in the published wheel, so use a source checkout if you want the bundled notebooks and demo scripts

## Docs

A lightweight static documentation site lives under `docs/` and is deployed through GitHub Pages.

- `docs/index.html`
- `docs/getting-started.html`
- `docs/architecture.html`
- `docs/api.html`

## Real LLM smoke test

Expected environment variables:
- `OPENAI_API_KEY`
- optional: `OPENAI_MODEL`
- optional: `OPENAI_BASE_URL`

Example provider usage:

```python
from kandor.builders.world_builder import WorldBuilder
from kandor.llm.openai import OpenAICompatibleLLM

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
python3 -m pip install 'kandor[widgets]'
```

Then in a notebook:

```python
from kandor import TemporalKGWidget
widget = TemporalKGWidget('reports/smoke/openai-smoke-kg-2026-03-24.json')
widget
```

You can also load the snapshot data directly:

```python
from kandor import load_temporal_kg_snapshot

data = load_temporal_kg_snapshot("reports/smoke/openai-smoke-kg-2026-03-24.json")
```

## Minimal Usage

```python
from kandor import LoreGenerator, SimulationRunner, WorldBuilder
from kandor.llm.mock import MockLLM

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

## Source Repository Extras

Introduction:
The source repository also includes demo scripts, notebooks, and docs for local exploration.

Usage:
- clone the repository if you want `examples/demo.py`, `examples/smoke_openai.py`, or the bundled notebooks
- run `python3 scripts/check_installed_wheel.py` before a release to verify the built wheel from a clean environment

Current status:
- the published package is focused on the library itself
- repository extras are maintained as release validation and onboarding material
