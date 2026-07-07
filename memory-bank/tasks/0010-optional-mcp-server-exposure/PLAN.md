# Plan — Task 0010

> Optional stretch goal — only after 0001–0009 are delivered and polished.

1. Pick the MCP Python SDK (official `mcp` package), stdio transport; add as optional dependency (extra: `pip install .[mcp]`).
2. `src/retail_agent/mcp_server.py`: thin handlers delegating to `bq.py` (`sql_guard` → execute → `pii_mask`) and `golden.py` (`retrieve`).
3. Unit tests: handler-level — DML rejected, PII masked in returned rows, trio retrieval shape.
4. Manual verification from a real MCP client (Cursor/Claude): both tools, safety proven client-side; capture transcript in WORKLOG.
5. Docs: `docs/MCP.md` (run, register, examples) + HLD extensibility section update.
6. Version minor bump. Commit: `feat(mcp): expose guarded query and trio retrieval as MCP server (task 0010)`.
