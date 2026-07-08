"""Application configuration loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass, field
from os import environ, getenv
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_ALLOWED_TABLES = frozenset({"orders", "order_items", "products", "users"})
DEFAULT_DATASET = "bigquery-public-data.thelook_ecommerce"
DEFAULT_MAX_BYTES_BILLED = 1_073_741_824  # 1 GiB
DEFAULT_QUERY_LIMIT = 1000
DEFAULT_MCP_MAX_RESPONSE_ROWS = 100
DEFAULT_EMBEDDING_MIN_SIMILARITY = 0.35
DEFAULT_LLM_PROVIDER = "gemini"
DEFAULT_OPENROUTER_MODEL = "openrouter/auto"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the retail agent and BigQuery layer."""

    gcp_project_id: str | None
    google_api_key: str | None
    model: str
    embedding_model: str
    persona: str
    provider: str
    fallback_provider: str | None
    openrouter_api_key: str | None
    openrouter_model: str
    ollama_host: str
    ollama_model: str
    dataset_id: str
    reports_db_path: str | None
    personas_dir: str | None
    max_bytes_billed: int
    default_limit: int
    mcp_max_response_rows: int
    embedding_min_similarity: float
    allowed_tables: frozenset[str] = field(default=DEFAULT_ALLOWED_TABLES)


def get_settings(*, load_env: bool = True) -> Settings:
    """Load settings from the environment (and optional `.env` file)."""

    if load_env:
        _load_env_file()

    gcp_project_id = _resolve_gcp_project_id()
    if gcp_project_id:
        # Google auth libraries read GOOGLE_CLOUD_PROJECT, not GCP_PROJECT_ID.
        environ.setdefault("GOOGLE_CLOUD_PROJECT", gcp_project_id)

    return Settings(
        gcp_project_id=gcp_project_id,
        google_api_key=_optional_str("GOOGLE_API_KEY"),
        model=getenv("RETAIL_AGENT_MODEL", "gemini-2.5-flash"),
        embedding_model=getenv("RETAIL_AGENT_EMBEDDING_MODEL", "gemini-embedding-001"),
        persona=getenv("RETAIL_AGENT_PERSONA", "default"),
        provider=getenv("RETAIL_AGENT_PROVIDER", DEFAULT_LLM_PROVIDER),
        fallback_provider=_optional_str("RETAIL_AGENT_FALLBACK_PROVIDER"),
        openrouter_api_key=_optional_str("OPENROUTER_API_KEY"),
        openrouter_model=getenv("RETAIL_AGENT_OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
        ollama_host=getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST),
        ollama_model=getenv("RETAIL_AGENT_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
        dataset_id=getenv("BQ_DATASET_ID", DEFAULT_DATASET),
        reports_db_path=_optional_str("RETAIL_AGENT_DB_PATH"),
        personas_dir=_optional_str("RETAIL_AGENT_PERSONAS_DIR"),
        max_bytes_billed=_int_env("BQ_MAX_BYTES_BILLED", DEFAULT_MAX_BYTES_BILLED),
        default_limit=_int_env("BQ_DEFAULT_LIMIT", DEFAULT_QUERY_LIMIT),
        mcp_max_response_rows=_int_env(
            "MCP_MAX_RESPONSE_ROWS",
            DEFAULT_MCP_MAX_RESPONSE_ROWS,
        ),
        embedding_min_similarity=_float_env(
            "GOLDEN_EMBEDDING_MIN_SIMILARITY",
            DEFAULT_EMBEDDING_MIN_SIMILARITY,
        ),
    )


def _load_env_file() -> None:
    """Load `.env` from the repository root (works regardless of shell cwd)."""

    repo_root = Path(__file__).resolve().parents[2]
    env_path = repo_root / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)
        return
    load_dotenv(override=False)


def _resolve_gcp_project_id() -> str | None:
    """Resolve billing project from env (supports GCP and Google SDK variable names)."""

    for name in ("GCP_PROJECT_ID", "GOOGLE_CLOUD_PROJECT"):
        value = _optional_str(name)
        if value:
            return value
    return None


def _optional_str(name: str) -> str | None:
    value = getenv(name)
    return value if value else None


def _int_env(name: str, default: int) -> int:
    raw = getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _float_env(name: str, default: float) -> float:
    raw = getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)
