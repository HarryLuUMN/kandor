from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import anywidget
    import traitlets
except ImportError:  # pragma: no cover
    anywidget = None
    traitlets = None


def load_temporal_kg_snapshot(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _esm_source() -> str:
    return (Path(__file__).with_name("temporal_kg.js")).read_text(encoding="utf-8")


if anywidget is not None and traitlets is not None:
    class TemporalKGWidget(anywidget.AnyWidget):
        _esm = _esm_source()

        data = traitlets.Dict().tag(sync=True)
        time = traitlets.Int(allow_none=True, default_value=None).tag(sync=True)
        min_time = traitlets.Int(default_value=0).tag(sync=True)
        max_time = traitlets.Int(default_value=0).tag(sync=True)

        def __init__(self, data: dict[str, Any] | str | Path, *, time: int | None = None) -> None:
            if isinstance(data, (str, Path)):
                data = load_temporal_kg_snapshot(data)
            relations = data.get("relations", [])
            events = data.get("events", [])
            times = []
            for relation in relations:
                if "start_time" in relation:
                    times.append(relation["start_time"])
                if relation.get("end_time") is not None:
                    times.append(relation["end_time"])
            for event in events:
                if "timestamp" in event:
                    times.append(event["timestamp"])
            min_time = min(times) if times else 0
            max_time = max(times) if times else 0
            super().__init__(
                data=data,
                time=max_time if time is None else time,
                min_time=min_time,
                max_time=max_time,
            )
else:
    class TemporalKGWidget:  # pragma: no cover
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise ImportError("TemporalKGWidget requires anywidget and traitlets")
