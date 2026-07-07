"""Baseline loading and regression comparison for eval runs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from retail_agent.evals.cases import evals_root


@dataclass
class Regression:
    case_id: str
    message: str


@dataclass
class BaselineComparison:
    regressions: list[Regression] = field(default_factory=list)

    @property
    def has_regressions(self) -> bool:
        return bool(self.regressions)


def default_baseline_path() -> Path:
    return evals_root() / "baseline" / "dry-run-v0.8.0.jsonl"


def load_baseline(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    baseline: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        if record.get("type") == "summary":
            continue
        baseline[record["case_id"]] = record
    return baseline


def compare_runs(
    current: list[dict],
    baseline: dict[str, dict],
    *,
    score_tolerance: int = 1,
) -> BaselineComparison:
    regressions: list[Regression] = []
    current_by_id = {record["case_id"]: record for record in current if record.get("case_id")}

    for case_id, base in baseline.items():
        now = current_by_id.get(case_id)
        if now is None:
            regressions.append(Regression(case_id, "missing from current run"))
            continue
        if base.get("passed") and not now.get("passed"):
            regressions.append(Regression(case_id, "passed -> failed"))
            continue
        base_score = base.get("judge_score")
        now_score = now.get("judge_score")
        if base_score is not None and now_score is not None and now_score < base_score - score_tolerance:
            regressions.append(
                Regression(
                    case_id,
                    f"judge score dropped {base_score} -> {now_score}",
                )
            )
    return BaselineComparison(regressions=regressions)


def write_run_records(path: Path, records: list[dict], *, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
        handle.write(json.dumps({"type": "summary", **summary}) + "\n")
