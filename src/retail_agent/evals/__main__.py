"""CLI entry point for the QA evaluation suite."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from retail_agent.evals.baseline import default_baseline_path, write_run_records
from retail_agent.evals.cases import evals_root
from retail_agent.evals.runner import format_summary, run_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the retail agent QA evaluation suite")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run against live LLM and BigQuery (requires credentials)",
    )
    parser.add_argument(
        "--layer",
        choices=["all", "capability", "safety"],
        default="all",
        help="Subset of eval cases to run",
    )
    parser.add_argument(
        "--baseline",
        default=str(default_baseline_path()),
        help="Baseline JSONL file for regression comparison",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output path for this run's JSONL results",
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        help="Skip baseline regression comparison",
    )
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="Skip LLM-as-judge intent scoring",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Overwrite the baseline file with this run's results",
    )
    args = parser.parse_args(argv)

    summary = run_suite(
        live=args.live,
        layer=args.layer,
        baseline_path=Path(args.baseline),
        output_path=Path(args.output) if args.output else None,
        compare_baseline=not args.no_compare and not args.update_baseline,
        with_judge=not args.no_judge,
    )
    print(format_summary(summary))

    if args.update_baseline:
        records = [
            {
                "case_id": item.case_id,
                "layer": item.layer,
                "passed": item.passed,
                "judge_score": item.judge_score,
            }
            for item in summary.results
        ]
        write_run_records(
            Path(args.baseline),
            records,
            summary={
                "mode": summary.mode,
                "total": summary.total,
                "passed": summary.passed,
                "failed": summary.failed,
                "avg_judge_score": summary.avg_judge_score,
            },
        )
        print(f"\nBaseline updated at {args.baseline}")

    if summary.failed or summary.regressions:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
