# Plan for V1 Python Library

## Goal

Build a Python library for LLM-based world building with:

- a `GodAgent` that compiles user intent into a structured world specification
- a simulation engine that advances the world over time
- a temporal knowledge graph as the long-term memory layer
- retrieval utilities that expose state, history, and entity-level memory to agents

The first version should prioritize:

- clear abstractions over breadth
- deterministic core data flow
- easy local testing
- provider-agnostic LLM integration

## V1 Product Shape

The library should feel like an SDK, not an app.

Users of the library should be able to:

1. define or generate a world spec
2. initialize a world state
3. run one or more simulation steps
4. store world events and state changes in temporal KG memory
5. query the world at a given time
6. generate summaries or lore from structured memory

Example target usage:

```python
from sim_llm_game import WorldBuilder, SimulationRunner

builder = WorldBuilder(llm=my_llm)
world = builder.create_world(
    prompt="Create a fractured fantasy world with trade cities, old religions, and rising machine magic."
)

runner = SimulationRunner(world=world, llm=my_llm)
runner.step()
runner.step()

snapshot = runner.memory.get_world_state_at(time=2)
history = runner.memory.get_entity_history("kingdom.red_coast")
```

## V1 Scope

Include:

- one central `GodAgent`
- one centralized simulation loop
- a temporal KG memory model
- structured retrieval APIs
- summary generation from retrieved memory
- pluggable LLM backend interface

Do not include in V1:

- many fully autonomous long-running agents
- multiplayer or web UI
- map generation
- distributed execution
- advanced planning/search pipelines
- training or fine-tuning

## Core Design Principle

The system should separate:

- world rules
- world state
- world events
- memory storage
- language generation

The LLM should guide specification, event proposal, and narration.
The library code should own validation, state transitions, memory writes, and retrieval.

## Proposed Package Structure

```text
sim_llm_game/
  __init__.py
  agents/
    __init__.py
    god_agent.py
  core/
    __init__.py
    models.py
    types.py
    exceptions.py
  memory/
    __init__.py
    temporal_kg.py
    retrieval.py
    summaries.py
  simulation/
    __init__.py
    engine.py
    rules.py
    events.py
    updater.py
  llm/
    __init__.py
    base.py
    mock.py
  builders/
    __init__.py
    world_builder.py
  generation/
    __init__.py
    lore.py
  prompts/
    god_agent.yaml
    event_proposal.yaml
    lore_summary.yaml
  tests/
    test_temporal_kg.py
    test_simulation_engine.py
    test_world_builder.py
```

## Main Domain Objects

Suggested core models:

- `WorldSpec`
  - genre
  - rules
  - ontology
  - simulation parameters
- `Entity`
  - id
  - type
  - attributes
- `Relation`
  - subject
  - predicate
  - object
  - valid_time
- `Event`
  - id
  - type
  - timestamp
  - participants
  - effects
- `WorldState`
  - current_time
  - active entities
  - derived state cache
- `MemoryRecord`
  - fact or event payload
  - source
  - timestamp or interval

Use `pydantic` models for V1 to keep validation simple and explicit.

## Temporal KG Design

The temporal KG should be the canonical memory layer.

Represent two kinds of memory:

1. State facts
   - example: `city.alpha controlled_by kingdom.red @ [5, 8]`
2. Events
   - example: `battle.fall_of_alpha occurred_at city.alpha @ 8`

Recommended V1 temporal representation:

- discrete integer ticks for time
- support both point-in-time and interval facts
- store event records separately from persistent relations

Minimal triple shape:

- `subject`
- `predicate`
- `object`
- `start_time`
- `end_time`
- `metadata`

Required queries:

- `get_world_state_at(time)`
- `get_entity_history(entity_id)`
- `get_active_relations(entity_id, time=None)`
- `get_events_between(start, end)`
- `get_relevant_context(entity_ids, time, horizon)`

## Retrieval Design

Retrieval should be task-oriented rather than generic.

Provide:

- state retrieval for current simulation
- historical retrieval for causal reasoning
- entity dossier retrieval for generation
- summary retrieval for prompt compression

V1 retrieval output should be structured Python objects first, not raw prompt text.

## God Agent Responsibilities

The `GodAgent` should transform user input into:

- world premise
- ontology
- initial entities
- initial relations
- simulation rules
- seed tensions or open conflicts

The `GodAgent` should not directly run the whole simulation.
It should act as the compiler for the world setup.

## Simulation Engine Design

The simulation engine should be centralized and step-based.

Single step flow:

1. read current world state from memory
2. retrieve relevant entities, tensions, and recent history
3. propose candidate events
4. validate event consistency against world rules
5. choose event(s) to apply
6. update state and relations
7. write changes into temporal KG
8. optionally generate summaries

This keeps the system inspectable and easy to test.

## Event Model

V1 should treat events as the main driver of world change.

Useful starter event types:

- alliance formed
- alliance broken
- war started
- battle occurred
- ruler changed
- city founded
- resource shortage
- religious schism
- discovery or invention

Each event should define:

- preconditions
- world effects
- affected entities
- textual summary

## LLM Abstraction

Use a provider-agnostic interface.

Suggested minimal interface:

```python
class BaseLLM:
    def generate_structured(self, prompt_name: str, variables: dict, schema: type):
        ...
```

V1 should ship with:

- `BaseLLM`
- `MockLLM` for tests

Adapters for OpenAI or other providers can be added after the core architecture is stable.

## Prompt Strategy

Per repository rules, prompts should live in `prompts/` as `.yaml` files.

V1 prompt files:

- `prompts/god_agent.yaml`
- `prompts/event_proposal.yaml`
- `prompts/lore_summary.yaml`

Each prompt file should define:

- purpose
- required inputs
- output schema expectations
- guardrails for consistency

## Public API Goals

The public API should be small and readable.

Suggested main entry points:

- `WorldBuilder`
- `SimulationRunner`
- `TemporalKGMemory`
- `GodAgent`

Avoid exposing too many low-level internals in V1.

## Testing Strategy

V1 should be test-first around deterministic pieces.

Prioritize tests for:

- temporal fact insertion and interval closing
- retrieval correctness at different times
- event application logic
- invalid event rejection
- world initialization from a structured spec
- simulation step with mocked LLM outputs

Use `pytest`.

## Suggested Build Order

Phase 1:

- initialize package structure
- add core models
- add temporal KG memory
- add tests for memory and retrieval

Phase 2:

- implement simulation event model
- implement state updater
- implement centralized simulation runner
- add deterministic tests

Phase 3:

- add `GodAgent`
- add prompt YAML files
- add structured world creation flow

Phase 4:

- add lore generation and summaries
- improve API ergonomics
- write examples and docs

## Recommended V1 Dependencies

Keep dependencies light:

- `pydantic`
- `pytest`
- `pyyaml`

Optional later:

- `networkx` if graph utilities become useful
- provider SDKs such as `openai`

## Risks to Watch

- overly flexible ontology causing unstable outputs
- LLM-generated events violating hard rules
- time representation becoming too complex too early
- prompt outputs drifting away from schema
- retrieval returning too much fragmented context

## Recommendation

The best first implementation is:

- one Python package
- one central `GodAgent`
- one deterministic step-based simulation engine
- one temporal KG memory backend
- one mockable LLM interface

That version is small enough to finish, but strong enough to validate the core thesis:
temporal KG memory can support more coherent long-term world simulation than text-only memory.
