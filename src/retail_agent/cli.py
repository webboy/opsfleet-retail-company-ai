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

HELP_TEXT = """
Commands:
  /help  Show this help
  /save  Save the most recent report to your library
  /exit  Exit the chat (also /quit)

Ask natural-language questions about retail sales, products, customers, or the database schema.
Saved report commands include "show my reports" and "delete reports mentioning <term>".
""".strip()


def run_repl(*, user_id: str, thread_id: str | None = None, deps: AgentDeps | None = None) -> int:
    deps = deps or AgentDeps.create()
    checkpointer = MemorySaver()
    graph = compile_graph(deps, checkpointer=checkpointer)
    thread_id = thread_id or f"{user_id}-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    awaiting_interrupt = False

    print(f"Retail Agent CLI — user={user_id} thread={thread_id}")
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

        question = "save this report" if user_input == "/save" else user_input

        try:
            if awaiting_interrupt:
                result = graph.invoke(Command(resume=question), config)
                awaiting_interrupt = False
            else:
                result = graph.invoke(
                    {
                        "messages": [HumanMessage(content=question)],
                        "user_id": user_id,
                        "question": question,
                    },
                    config,
                )

            snapshot = graph.get_state(config)
            if snapshot.next:
                awaiting_interrupt = True
                if not _print_interrupt_prompt(snapshot):
                    print("\nAgent: Please confirm or cancel.\n")
                continue

            report = result.get("report") or "I couldn't produce an answer for that question."
            print(f"\nAgent: {report}\n")
            if result.get("sql"):
                attempts = result.get("sql_attempts", 0)
                print(f"[sql attempts={attempts}]\n")
            if result.get("retrieved_trio_ids"):
                method = result.get("retrieval_method", "unknown")
                print(f"[retrieved trios={result['retrieved_trio_ids']} method={method}]\n")
        except Exception:  # noqa: BLE001 — never leak stack traces in CLI
            logging.exception("CLI turn failed")
            awaiting_interrupt = False
            print(
                "\nAgent: Sorry, something went wrong while processing your question. "
                "Please try again or rephrase your question.\n"
            )


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
