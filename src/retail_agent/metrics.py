"""CLI to summarize observability metrics from JSONL events."""

from __future__ import annotations

import argparse
import json
import sys

from retail_agent.observability import DEFAULT_EVENTS_PATH, aggregate_metrics, load_events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate agent observability metrics")
    parser.add_argument(
        "--log-path",
        default=str(DEFAULT_EVENTS_PATH),
        help="Path to agent_events.jsonl",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print metrics as JSON instead of a human-readable summary",
    )
    args = parser.parse_args(argv)

    events = load_events(args.log_path)
    metrics = aggregate_metrics(events)
    if args.json:
        print(json.dumps(metrics, indent=2))
        return 0

    print("Agent metrics summary")
    print(f"  turns: {metrics['total_turns']}")
    print(f"  success_rate: {metrics['turn_success_rate']:.1%}")
    print(f"  fallback_rate: {metrics['fallback_rate']:.1%}")
    print(f"  guard_block_rate: {metrics['guard_block_rate']:.1%}")
    print(f"  self_heal_events: {metrics['self_heal_events']}")
    print(f"  pii_mask_hits: {metrics['pii_mask_hits']}")
    print(f"  latency_ms: p50={metrics['latency_ms']['p50']} p95={metrics['latency_ms']['p95']}")
    if metrics["error_classes"]:
        print(f"  error_classes: {metrics['error_classes']}")
    if metrics["turn_outcomes"]:
        print(f"  turn_outcomes: {metrics['turn_outcomes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
