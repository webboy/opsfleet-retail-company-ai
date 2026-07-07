"""CLI to reconstruct one turn from structured JSONL events."""

from __future__ import annotations

import argparse
import sys

from retail_agent.observability import DEFAULT_EVENTS_PATH, events_for_turn, format_trace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reconstruct one agent turn from JSONL events")
    parser.add_argument("turn_id", help="Turn id to inspect")
    parser.add_argument(
        "--log-path",
        default=str(DEFAULT_EVENTS_PATH),
        help="Path to agent_events.jsonl",
    )
    args = parser.parse_args(argv)

    events = events_for_turn(args.turn_id, log_path=args.log_path)
    if not events:
        print(f"No events found for turn_id={args.turn_id}", file=sys.stderr)
        return 1
    print(format_trace(events))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
