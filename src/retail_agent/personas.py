"""Load report tone/persona instructions from editable files."""

from __future__ import annotations

import re
from pathlib import Path

_PERSONA_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def load_persona(name: str, *, personas_dir: Path | str | None = None) -> str:
    safe_name = _safe_persona_name(name)
    base = Path(personas_dir or _default_personas_dir())
    for suffix in (".md", ".yaml", ".yml"):
        path = base / f"{safe_name}{suffix}"
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    raise FileNotFoundError(f"Persona '{safe_name}' not found in {base}")


def list_persona_names(*, personas_dir: Path | str | None = None) -> list[str]:
    base = Path(personas_dir or _default_personas_dir())
    if not base.is_dir():
        return []
    names: set[str] = set()
    for path in base.iterdir():
        if path.suffix.lower() in {".md", ".yaml", ".yml"} and path.is_file():
            names.add(path.stem)
    return sorted(names)


def _safe_persona_name(name: str) -> str:
    cleaned = (name or "").strip()
    if not cleaned or not _PERSONA_NAME_RE.fullmatch(cleaned):
        raise ValueError(f"Invalid persona name: {name!r}")
    return cleaned


def _default_personas_dir() -> Path:
    from os import getenv

    configured = getenv("RETAIL_AGENT_PERSONAS_DIR")
    if configured:
        return Path(configured)
    return Path.cwd() / "personas"
