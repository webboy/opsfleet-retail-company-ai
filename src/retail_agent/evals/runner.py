"""Eval suite runner for capability, safety, and intent scoring."""

from __future__ import annotations

import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from retail_agent.config import Settings, get_settings
from retail_agent.deps import AgentDeps
from retail_agent.evals.assertions import evaluate_expectations
from retail_agent.evals.baseline import (
    BaselineComparison,
    compare_runs,
    default_baseline_path,
    write_run_records,
)
from retail_agent.evals.cases import EvalCase, EvalStep, evals_root, load_cases
from retail_agent.evals.fakes import FakeBQRunner, ScriptLLM, query_result_from_spec
from retail_agent.evals.judge import score_intent
from retail_agent.golden import FakeEmbedder, TrioStore
from retail_agent.graph import compile_graph
from retail_agent.observability import TurnTracer
from retail_agent.stores import ReportStore


@dataclass
class CaseResult:
    case_id: str
    layer: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    judge_score: int | None = None
    judge_rationale: str = ""
    turn_id: str | None = None


@dataclass
class EvalSummary:
    mode: str
    total: int
    passed: int
    failed: int
    avg_judge_score: float | None
    results: list[CaseResult] = field(default_factory=list)
    regressions: list[str] = field(default_factory=list)


def run_suite(
    *,
    live: bool = False,
    layer: str = "all",
    baseline_path: Path | None = None,
    output_path: Path | None = None,
    compare_baseline: bool = True,
    with_judge: bool = True,
) -> EvalSummary:
    cases = load_cases(layer=layer)
    temp_dir = tempfile.TemporaryDirectory()
    work_dir = Path(temp_dir.name)
    settings = _build_settings(work_dir, live=live)
    results: list[CaseResult] = []

    for case in cases:
        deps = _build_deps(case, settings=settings, live=live, work_dir=work_dir)
        result = _run_case(case, deps)
        if with_judge and case.judge and case.layer == "capability" and result.passed:
            score, rationale = score_intent(
                result.state,
                question=case.question or "",
                settings=settings,
                llm=None if not live else deps.llm,
                dry_run=None if live else case.dry_run,
            )
            result.judge_score = score
            result.judge_rationale = rationale
            if score is not None and score < 3:
                result.passed = False
                result.failures.append(f"judge score too low: {score}")
        results.append(result)

    summary = _summarize(results, mode="live" if live else "dry-run")
    records = [_result_record(item) for item in results]
    run_path = output_path or (evals_root() / "runs" / f"{summary.mode}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl")
    write_run_records(
        run_path,
        records,
        summary={
            "mode": summary.mode,
            "total": summary.total,
            "passed": summary.passed,
            "failed": summary.failed,
            "avg_judge_score": summary.avg_judge_score,
        },
    )

    if compare_baseline:
        baseline = default_baseline_path() if baseline_path is None else baseline_path
        comparison: BaselineComparison = compare_runs(records, _load_baseline_map(baseline))
        summary.regressions = [f"{item.case_id}: {item.message}" for item in comparison.regressions]

    temp_dir.cleanup()
    return summary


def _summarize(results: list[CaseResult], *, mode: str) -> EvalSummary:
    passed = sum(1 for item in results if item.passed)
    scores = [item.judge_score for item in results if item.judge_score is not None]
    avg = round(sum(scores) / len(scores), 2) if scores else None
    return EvalSummary(
        mode=mode,
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        avg_judge_score=avg,
        results=results,
    )


def _result_record(item: CaseResult) -> dict:
    return {
        "case_id": item.case_id,
        "layer": item.layer,
        "passed": item.passed,
        "failures": item.failures,
        "judge_score": item.judge_score,
        "judge_rationale": item.judge_rationale,
        "turn_id": item.turn_id,
    }


def _load_baseline_map(path: Path) -> dict[str, dict]:
    from retail_agent.evals.baseline import load_baseline

    return load_baseline(path)


def _build_settings(work_dir: Path, *, live: bool) -> Settings:
    if live:
        return get_settings()
    return Settings(
        gcp_project_id="eval-project",
        google_api_key="eval-key",
        model="gemini-2.5-flash",
        embedding_model="gemini-embedding-001",
        persona="default",
        provider="gemini",
        fallback_provider=None,
        openrouter_api_key=None,
        openrouter_model="google/gemini-2.0-flash-exp:free",
        ollama_host="http://localhost:11434",
        ollama_model="llama3.2",
        dataset_id="bigquery-public-data.thelook_ecommerce",
        reports_db_path=str(work_dir / "reports.sqlite3"),
        personas_dir=None,
        max_bytes_billed=1_073_741_824,
        default_limit=1000,
    )


def _build_deps(case: EvalCase, *, settings: Settings, live: bool, work_dir: Path) -> AgentDeps:
    bucket_dir = work_dir / "golden_bucket"
    if live:
        bucket_dir = evals_root().parent / "golden_bucket"
    else:
        shutil.copytree(evals_root().parent / "golden_bucket", bucket_dir, dirs_exist_ok=True)
        (bucket_dir / "candidates").mkdir(exist_ok=True)

    if live:
        return AgentDeps.create(settings=settings)

    dry_run = case.dry_run
    llm = ScriptLLM(dry_run.get("llm_responses") or ["Fallback response"])
    bq = FakeBQRunner([query_result_from_spec(item) for item in dry_run.get("bq_outcomes") or []])
    report_store = ReportStore(db_path=settings.reports_db_path)
    for saved in case.setup.get("saved_reports") or []:
        report_store.save_report(
            owner=saved.get("owner", "alice"),
            title=saved.get("title", "Saved report"),
            content=saved.get("content", "content"),
        )
    return AgentDeps(
        settings=settings,
        llm=llm,
        bq_runner=bq,
        trio_store=TrioStore(bucket_dir, settings=settings, embedder=FakeEmbedder()),
        report_store=report_store,
    )


@dataclass
class _InternalCaseResult(CaseResult):
    state: dict = field(default_factory=dict)


def _run_case(case: EvalCase, deps: AgentDeps) -> _InternalCaseResult:
    graph = compile_graph(deps)
    thread_id = f"eval-{case.id}-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    turn_id = uuid.uuid4().hex
    deps.tracer = TurnTracer(
        turn_id=turn_id,
        user_id="alice",
        thread_id=thread_id,
        provider=deps.settings.provider,
        model=deps.settings.model,
    )

    if case.steps:
        return _run_steps_case(case, graph, deps, config, turn_id)

    question = case.question or ""
    deps.tracer.emit_turn_start(question)
    state = graph.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "user_id": "alice",
            "question": question,
        },
        config,
    )
    deps.tracer.emit_turn_end(status=state.get("status"), report=state.get("report"))
    assertion = evaluate_expectations(
        state,
        case.expect,
        bq_calls=getattr(deps.bq_runner, "calls", 0),
        llm_calls=getattr(deps.llm, "calls", 0),
    )
    return _InternalCaseResult(
        case_id=case.id,
        layer=case.layer,
        passed=assertion.passed,
        failures=assertion.failures,
        turn_id=turn_id,
        state=state,
    )


def _run_steps_case(case: EvalCase, graph, deps: AgentDeps, config: dict, turn_id: str) -> _InternalCaseResult:
    failures: list[str] = []
    final_state: dict = {}
    interrupted = False

    for index, step in enumerate(case.steps):
        setup = {**case.setup, **step.setup}
        for saved in setup.get("saved_reports") or []:
            deps.report_store.save_report(
                owner=saved.get("owner", "alice"),
                title=saved.get("title", "Saved report"),
                content=saved.get("content", "content"),
            )

        if index == 0 and step.question:
            deps.tracer.emit_turn_start(step.question)

        if step.resume:
            final_state = graph.invoke(Command(resume=step.resume), config)
        else:
            final_state = graph.invoke(
                {
                    "messages": [HumanMessage(content=step.question or "")],
                    "user_id": "alice",
                    "question": step.question or "",
                },
                config,
            )

        interrupted = bool(graph.get_state(config).next)
        assertion = evaluate_expectations(
            final_state,
            step.expect,
            bq_calls=getattr(deps.bq_runner, "calls", 0),
            llm_calls=getattr(deps.llm, "calls", 0),
            interrupted=interrupted,
        )
        if not assertion.passed:
            failures.extend(assertion.failures)

    if not interrupted:
        deps.tracer.emit_turn_end(status=final_state.get("status"), report=final_state.get("report"))

    return _InternalCaseResult(
        case_id=case.id,
        layer=case.layer,
        passed=not failures,
        failures=failures,
        turn_id=turn_id,
        state=final_state,
    )


def format_summary(summary: EvalSummary) -> str:
    lines = [
        f"Eval mode: {summary.mode}",
        f"Cases: {summary.total} passed={summary.passed} failed={summary.failed}",
    ]
    if summary.avg_judge_score is not None:
        lines.append(f"Avg judge score: {summary.avg_judge_score}")
    lines.append("")
    for item in summary.results:
        status = "PASS" if item.passed else "FAIL"
        extra = f" score={item.judge_score}" if item.judge_score is not None else ""
        lines.append(f"[{status}] {item.case_id}{extra}")
        for failure in item.failures:
            lines.append(f"  - {failure}")
    if summary.regressions:
        lines.append("")
        lines.append("Regressions:")
        for regression in summary.regressions:
            lines.append(f"  - {regression}")
    return "\n".join(lines)
