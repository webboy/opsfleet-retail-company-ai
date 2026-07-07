"""Load eval case definitions from YAML assets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class EvalStep:
    question: str | None = None
    resume: str | None = None
    setup: dict = field(default_factory=dict)
    expect: dict = field(default_factory=dict)


@dataclass
class EvalCase:
    id: str
    layer: str
    question: str | None = None
    steps: list[EvalStep] = field(default_factory=list)
    setup: dict = field(default_factory=dict)
    dry_run: dict = field(default_factory=dict)
    expect: dict = field(default_factory=dict)
    judge: bool = True


def evals_root() -> Path:
    return Path(__file__).resolve().parents[3] / "evals"


def cases_path() -> Path:
    return evals_root() / "cases.yaml"


def judge_prompt_path() -> Path:
    return evals_root() / "judge_prompt.md"


def load_cases(*, layer: str = "all") -> list[EvalCase]:
    raw = yaml.safe_load(cases_path().read_text(encoding="utf-8")) or []
    cases = [_parse_case(item) for item in raw]
    if layer == "all":
        return cases
    return [case for case in cases if case.layer == layer]


def _parse_case(item: dict) -> EvalCase:
    steps = [
        EvalStep(
            question=step.get("question"),
            resume=step.get("resume"),
            setup=step.get("setup") or {},
            expect=step.get("expect") or {},
        )
        for step in item.get("steps") or []
    ]
    return EvalCase(
        id=item["id"],
        layer=item["layer"],
        question=item.get("question"),
        steps=steps,
        setup=item.get("setup") or {},
        dry_run=item.get("dry_run") or {},
        expect=item.get("expect") or {},
        judge=item.get("judge", True),
    )
