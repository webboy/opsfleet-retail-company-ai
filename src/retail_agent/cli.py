"""Interactive CLI for the retail analysis agent."""

from __future__ import annotations

import argparse
import logging
import sys
import uuid

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from retail_agent.deps import AgentDeps
from retail_agent.graph import compile_graph

HELP_TEXT = """
Commands:
  /help  Show this help
  /exit  Exit the chat (also /quit)

Ask natural-language questions about retail sales, products, customers, or the database schema.
""".strip()


def run_repl(*, user_id: str, thread_id: str | None = None, deps: AgentDeps | None = None) -> int:
    deps = deps or AgentDeps.create()
    checkpointer = MemorySaver()
    graph = compile_graph(deps, checkpointer=checkpointer)
    thread_id = thread_id or f"{user_id}-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

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

        try:
            result = graph.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "user_id": user_id,
                    "question": user_input,
                },
                config,
            )
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
            print(
                "\nAgent: Sorry, something went wrong while processing your question. "
                "Please try again or rephrase your question.\n"
            )


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
