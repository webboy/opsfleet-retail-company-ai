"""Structured JSONL observability for agent turns and node executions."""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from retail_agent.llm import get_fallback_metadata
from retail_agent.state import AgentState

DEFAULT_EVENTS_PATH = Path("logs/agent_events.jsonl")

SAFE_STATE_FIELDS = (
    "user_id",
    "question",
    "turn_mode",
    "guard_decision",
    "guard_route",
    "guard_reason",
    "pii_masked",
    "pii_mask_hits",
    "pii_masked_columns",
    "retrieved_trio_ids",
    "retrieval_method",
    "candidate_captured",
    "sql",
    "sql_attempts",
    "max_sql_attempts",
    "last_error",
    "query_ok",
    "query_empty",
    "status",
    "report_action",
    "report_selector_kind",
    "preference_action",
    "preference_output_format",
    "persona_name",
)


def snapshot_state(state: AgentState | dict[str, Any] | None) -> dict[str, Any]:
    """Return a safe, JSON-serializable subset of graph state."""

    if not state:
        return {}
    snapshot: dict[str, Any] = {}
    for key in SAFE_STATE_FIELDS:
        if key in state:
            snapshot[key] = state[key]
    budget = state.get("llm_budget")
    if budget:
        snapshot["llm_budget"] = budget
    report = state.get("report")
    if isinstance(report, str):
        snapshot["report_excerpt"] = _excerpt(report, limit=240)
    return snapshot


def classify_error(state: AgentState | dict[str, Any] | None) -> str | None:
    if not state:
        return None
    if state.get("guard_decision") == "refused":
        return "guard_refused"
    if state.get("status") == "fallback":
        last_error = (state.get("last_error") or "").lower()
        if "budget" in last_error:
            return "budget_exhausted"
        if state.get("query_ok") is False or state.get("last_error"):
            return "sql_failed"
        if state.get("query_empty"):
            return "empty_result"
        return "fallback"
    if state.get("last_error"):
        return "node_error"
    return None


def _excerpt(text: str, *, limit: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TurnTracer:
    """Append-only JSONL tracer for one logical user turn."""

    turn_id: str
    user_id: str
    thread_id: str | None = None
    log_path: Path = field(default_factory=lambda: DEFAULT_EVENTS_PATH)
    provider: str | None = None
    model: str | None = None
    question: str | None = None

    def emit(self, event_type: str, **fields: Any) -> dict[str, Any]:
        event = {
            "timestamp": _utc_now(),
            "event_type": event_type,
            "turn_id": self.turn_id,
            "user_id": self.user_id,
            "thread_id": self.thread_id,
            "provider": self.provider,
            "model": self.model,
            **fields,
        }
        self._append(event)
        return event

    def emit_turn_start(self, question: str) -> dict[str, Any]:
        self.question = question
        return self.emit("turn_start", question=question)

    def emit_turn_end(self, *, status: str | None, report: str | None = None) -> dict[str, Any]:
        return self.emit(
            "turn_end",
            status=status,
            report_excerpt=_excerpt(report or "", limit=320),
            question=self.question,
        )

    def emit_node_event(
        self,
        node: str,
        *,
        latency_ms: float,
        state_before: dict[str, Any],
        state_after: dict[str, Any],
        error: str | None = None,
        fallback_metadata: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        return self.emit(
            "node",
            node=node,
            latency_ms=round(latency_ms, 2),
            state_before=state_before,
            state_after=state_after,
            error_class=error or classify_error(state_after),
            sql=state_after.get("sql"),
            sql_attempts=state_after.get("sql_attempts"),
            guard_decision=state_after.get("guard_decision"),
            guard_route=state_after.get("guard_route"),
            retrieved_trio_ids=state_after.get("retrieved_trio_ids"),
            retrieval_method=state_after.get("retrieval_method"),
            pii_mask_hits=state_after.get("pii_mask_hits"),
            status=state_after.get("status"),
            fallback_metadata=fallback_metadata or {},
        )

    def _append(self, event: dict[str, Any]) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, default=str) + "\n")


def load_events(log_path: Path | str = DEFAULT_EVENTS_PATH) -> list[dict[str, Any]]:
    path = Path(log_path)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        events.append(json.loads(line))
    return events


def events_for_turn(turn_id: str, *, log_path: Path | str = DEFAULT_EVENTS_PATH) -> list[dict[str, Any]]:
    return [event for event in load_events(log_path) if event.get("turn_id") == turn_id]


def merge_state(state: AgentState, update: dict[str, Any]) -> dict[str, Any]:
    merged = dict(state)
    merged.update(update)
    return merged


def aggregate_metrics(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary metrics from structured node/turn events."""

    node_events = [event for event in events if event.get("event_type") == "node"]
    turn_ends = {event["turn_id"]: event for event in events if event.get("event_type") == "turn_end"}
    turn_ids = sorted({event["turn_id"] for event in events if event.get("turn_id")})

    latencies = [float(event["latency_ms"]) for event in node_events if "latency_ms" in event]
    guard_blocks = sum(
        1
        for event in node_events
        if event.get("node") == "input_guard" and event.get("guard_decision") == "refused"
    )
    self_heals = sum(1 for event in node_events if int(event.get("sql_attempts") or 0) > 1)
    mask_hits = sum(int(event.get("pii_mask_hits") or 0) for event in node_events)

    outcomes: dict[str, int] = {}
    for turn_id in turn_ids:
        end = turn_ends.get(turn_id)
        status = end.get("status") if end else "unknown"
        outcomes[status or "unknown"] = outcomes.get(status or "unknown", 0) + 1

    error_classes: dict[str, int] = {}
    for event in node_events:
        error_class = event.get("error_class")
        if error_class:
            error_classes[error_class] = error_classes.get(error_class, 0) + 1

    total_turns = len(turn_ids)
    done_turns = outcomes.get("done", 0)
    fallback_turns = outcomes.get("fallback", 0)

    return {
        "total_turns": total_turns,
        "turn_success_rate": round(done_turns / total_turns, 3) if total_turns else 0.0,
        "fallback_rate": round(fallback_turns / total_turns, 3) if total_turns else 0.0,
        "guard_block_rate": round(guard_blocks / total_turns, 3) if total_turns else 0.0,
        "self_heal_events": self_heals,
        "pii_mask_hits": mask_hits,
        "error_classes": error_classes,
        "turn_outcomes": outcomes,
        "latency_ms": _latency_summary(latencies),
    }


def _latency_summary(latencies: list[float]) -> dict[str, float | int]:
    if not latencies:
        return {"count": 0, "p50": 0.0, "p95": 0.0}
    ordered = sorted(latencies)
    return {
        "count": len(ordered),
        "p50": round(statistics.median(ordered), 2),
        "p95": round(ordered[max(0, int(len(ordered) * 0.95) - 1)], 2),
    }


def format_trace(events: list[dict[str, Any]]) -> str:
    if not events:
        return "No events found for this turn."

    lines: list[str] = []
    turn_id = events[0].get("turn_id", "unknown")
    user_id = events[0].get("user_id", "unknown")
    lines.append(f"Turn {turn_id} (user={user_id})")
    lines.append("")

    for event in events:
        event_type = event.get("event_type")
        if event_type == "turn_start":
            lines.append(f"START question={event.get('question')!r}")
            continue
        if event_type == "turn_end":
            lines.append(
                f"END status={event.get('status')} report={event.get('report_excerpt')!r}"
            )
            continue
        if event_type != "node":
            continue
        parts = [
            f"- {event.get('node')}",
            f"{event.get('latency_ms')}ms",
            f"status={event.get('status')}",
        ]
        if event.get("guard_decision"):
            parts.append(f"guard={event.get('guard_decision')}")
        if event.get("sql_attempts"):
            parts.append(f"sql_attempts={event.get('sql_attempts')}")
        if event.get("retrieved_trio_ids"):
            parts.append(f"trios={event.get('retrieved_trio_ids')}")
        if event.get("pii_mask_hits"):
            parts.append(f"pii_hits={event.get('pii_mask_hits')}")
        if event.get("error_class"):
            parts.append(f"error={event.get('error_class')}")
        if event.get("sql"):
            parts.append(f"sql={_excerpt(str(event.get('sql')), limit=120)!r}")
        lines.append(" ".join(parts))

    return "\n".join(lines)


def traced_node(
    node_name: str,
    fn,
    deps,
    *,
    needs_deps: bool = True,
):
    """Wrap a graph node to emit structured observability events."""

    def run(state: AgentState) -> dict:
        tracer = getattr(deps, "tracer", None)
        if tracer is None:
            return fn(state, deps) if needs_deps else fn(state)

        started = time.perf_counter()
        before = snapshot_state(state)
        try:
            result = fn(state, deps) if needs_deps else fn(state)
            after = merge_state(state, result)
            latency_ms = (time.perf_counter() - started) * 1000
            tracer.emit_node_event(
                node_name,
                latency_ms=latency_ms,
                state_before=before,
                state_after=snapshot_state(after),
                fallback_metadata=get_fallback_metadata(deps.llm),
            )
            return result
        except Exception as exc:
            latency_ms = (time.perf_counter() - started) * 1000
            tracer.emit_node_event(
                node_name,
                latency_ms=latency_ms,
                state_before=before,
                state_after=snapshot_state(state),
                error=type(exc).__name__,
                fallback_metadata=get_fallback_metadata(deps.llm),
            )
            raise

    return run
