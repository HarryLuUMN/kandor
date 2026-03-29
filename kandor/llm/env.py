from __future__ import annotations

import os
from pathlib import Path


def load_dotenv_if_present(start: str | Path) -> None:
    path = Path(start).resolve()
    search_roots = [Path.cwd().resolve(), path, *path.parents]
    for candidate in search_roots:
        env_path = candidate / ".env"
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return
