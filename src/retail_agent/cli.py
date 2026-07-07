"""Interactive CLI for the retail analysis agent."""

from __future__ import annotations

import argparse
import logging
import sys
import uuid

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from retail_agent.deps import AgentDeps
from retail_agent.graph import compile_graph
from retail_agent.llm import is_quota_exhausted_error, quota_exhausted_message
from retail_agent.observability import DEFAULT_EVENTS_PATH, TurnTracer
from retail_agent.personas import list_persona_names, load_persona

HELP_TEXT = """
Commands:
  /help            Show this help
  /save            Save the most recent report to your library
  /prefs           Show your saved output preferences
  /persona <name>  Switch report tone for this session (e.g. default, formal, punchy)
  /exit            Exit the chat (also /quit)

Ask natural-language questions about retail sales, products, customers, or the database schema.
Saved report commands include "show my reports" and "delete reports mentioning <term>".
Preference examples: "I prefer tables from now on", "give me bullet points from now on".
""".strip()


def run_repl(*, user_id: str, thread_id: str | None = None, deps: AgentDeps | None = None) -> int:
    deps = deps or AgentDeps.create()
    checkpointer = MemorySaver()
    graph = compile_graph(deps, checkpointer=checkpointer)
    thread_id = thread_id or f"{user_id}-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    awaiting_interrupt = False
    session_persona = deps.settings.persona
    active_tracer: TurnTracer | None = None

    print(f"Retail Agent CLI — user={user_id} thread={thread_id}")
    print(f"Persona: {session_persona}")
    print("Type /help for commands.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not user_input:
            continue
        if user_input in {"/exit", "/quit"}:
            print("Goodbye.")
            return 0
        if user_input == "/help":
            print(HELP_TEXT)
            continue
        if user_input.startswith("/persona"):
            session_persona = _handle_persona_command(user_input, deps)
            continue

        question = user_input
        if user_input == "/save":
            question = "save this report"
        elif user_input == "/prefs":
            question = "show my preferences"

        try:
            if awaiting_interrupt:
                result = graph.invoke(Command(resume=question), config)
                awaiting_interrupt = False
            else:
                active_tracer = TurnTracer(
                    turn_id=uuid.uuid4().hex,
                    user_id=user_id,
                    thread_id=thread_id,
                    log_path=DEFAULT_EVENTS_PATH,
                    provider=deps.settings.provider,
                    model=deps.settings.model,
                )
                deps.tracer = active_tracer
                active_tracer.emit_turn_start(question)
                result = graph.invoke(
                    _invoke_context(user_id, session_persona, question=question),
                    config,
                )

            snapshot = graph.get_state(config)
            if snapshot.next:
                awaiting_interrupt = True
                if not _print_interrupt_prompt(snapshot):
                    print("\nAgent: Please confirm or cancel.\n")
                continue

            report = result.get("report") or "I couldn't produce an answer for that question."
            if active_tracer is not None:
                active_tracer.emit_turn_end(status=result.get("status"), report=report)
            print(f"\nAgent: {report}\n")
            if result.get("sql"):
                attempts = result.get("sql_attempts", 0)
                print(f"[sql attempts={attempts}]\n")
            if result.get("retrieved_trio_ids"):
                method = result.get("retrieval_method", "unknown")
                print(f"[retrieved trios={result['retrieved_trio_ids']} method={method}]\n")
        except Exception as exc:  # noqa: BLE001 — never leak stack traces in CLI
            if active_tracer is not None:
                active_tracer.emit_turn_end(status="fallback", report=str(exc))
            if is_quota_exhausted_error(exc):
                logging.warning("CLI turn blocked by Gemini quota exhaustion")
                print(
                    f"\nAgent: {quota_exhausted_message(model=deps.settings.model, provider=deps.settings.provider, fallback_provider=deps.settings.fallback_provider)}\n"
                )
            else:
                logging.exception("CLI turn failed")
                print(
                    "\nAgent: Sorry, something went wrong while processing your question. "
                    "Please try again or rephrase your question.\n"
                )
            awaiting_interrupt = False


def _invoke_context(
    user_id: str,
    persona_name: str,
    *,
    question: str | None = None,
) -> dict:
    payload = {
        "user_id": user_id,
        "persona_name": persona_name,
    }
    if question is not None:
        payload["messages"] = [HumanMessage(content=question)]
        payload["question"] = question
    return payload


def _handle_persona_command(user_input: str, deps: AgentDeps) -> str:
    parts = user_input.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        available = ", ".join(list_persona_names(personas_dir=deps.settings.personas_dir))
        print(f"\nAgent: Usage: /persona <name>. Available personas: {available}\n")
        return deps.settings.persona

    persona_name = parts[1].strip()
    try:
        load_persona(persona_name, personas_dir=deps.settings.personas_dir)
    except (FileNotFoundError, ValueError) as exc:
        available = ", ".join(list_persona_names(personas_dir=deps.settings.personas_dir))
        print(f"\nAgent: {exc}. Available personas: {available}\n")
        return deps.settings.persona

    print(f"\nAgent: Persona switched to '{persona_name}' for this session.\n")
    return persona_name


def _print_interrupt_prompt(snapshot) -> bool:
    for task in snapshot.tasks:
        interrupts = getattr(task, "interrupts", None) or ()
        for interrupt in interrupts:
            value = interrupt.value
            if isinstance(value, dict) and value.get("prompt"):
                print(f"\nAgent: {value['prompt']}\n")
                return True
            print(f"\nAgent: {value}\n")
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Retail data analysis chat agent")
    parser.add_argument("--user", required=True, help="User identity for this session")
    parser.add_argument(
        "--thread",
        default=None,
        help="Optional thread id for conversation memory (defaults to generated id)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        return run_repl(user_id=args.user, thread_id=args.thread)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
