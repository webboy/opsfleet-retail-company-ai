"""Unit tests for persona loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from retail_agent.personas import list_persona_names, load_persona


def test_load_persona_reads_markdown_file(tmp_path: Path):
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir()
    (personas_dir / "formal.md").write_text("Formal tone.", encoding="utf-8")

    assert load_persona("formal", personas_dir=personas_dir) == "Formal tone."


def test_load_persona_rejects_invalid_names(tmp_path: Path):
    with pytest.raises(ValueError):
        load_persona("../escape", personas_dir=tmp_path)


def test_list_persona_names(tmp_path: Path):
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir()
    (personas_dir / "default.md").write_text("Default", encoding="utf-8")
    (personas_dir / "punchy.yaml").write_text("name: punchy", encoding="utf-8")

    assert list_persona_names(personas_dir=personas_dir) == ["default", "punchy"]
