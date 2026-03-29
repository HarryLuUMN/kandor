from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import venv


REPO_ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd or REPO_ROOT, check=True)


def python_path(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def latest_wheel(dist_dir: Path) -> Path:
    return max(dist_dir.glob("kandor-*.whl"), key=lambda path: path.stat().st_mtime)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="kandor-wheel-check-") as tmp:
        tmp_path = Path(tmp)
        dist_dir = tmp_path / "dist"
        venv_dir = tmp_path / "venv"
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        run(sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "-w", str(dist_dir))

        venv.EnvBuilder(with_pip=True).create(venv_dir)
        venv_python = python_path(venv_dir)
        wheel_path = latest_wheel(dist_dir)

        run(str(venv_python), "-m", "pip", "install", f"{wheel_path}[widgets]")
        run(
            str(venv_python),
            "-c",
            (
                "from kandor import WorldBuilder; "
                "from kandor.llm.mock import MockLLM; "
                "llm = MockLLM(responses={'god_agent': {'premise': 'p', 'genre': 'g'}}); "
                "builder = WorldBuilder(llm=llm); "
                "blueprint = builder.create_world(prompt='x'); "
                "print(blueprint.spec.genre)"
            ),
            cwd=run_dir,
        )
        run(
            str(venv_python),
            "-c",
            (
                "from kandor.widgets.temporal_kg import _esm_source; "
                "source = _esm_source(); "
                "print(source[:40])"
            ),
            cwd=run_dir,
        )

        shutil.rmtree(venv_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
