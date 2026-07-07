"""Application configuration loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass, field
from os import environ, getenv

from dotenv import load_dotenv

DEFAULT_ALLOWED_TABLES = frozenset({"orders", "order_items", "products", "users"})
DEFAULT_DATASET = "bigquery-public-data.thelook_ecommerce"
DEFAULT_MAX_BYTES_BILLED = 1_073_741_824  # 1 GiB
DEFAULT_QUERY_LIMIT = 1000


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the retail agent and BigQuery layer."""

    gcp_project_id: str | None
    google_api_key: str | None
    model: str
    embedding_model: str
    persona: str
    dataset_id: str
    reports_db_path: str | None
    personas_dir: str | None
    max_bytes_billed: int
    default_limit: int
    allowed_tables: frozenset[str] = field(default=DEFAULT_ALLOWED_TABLES)


def get_settings(*, load_env: bool = True) -> Settings:
    """Load settings from the environment (and optional `.env` file)."""

    if load_env:
        load_dotenv()

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
        dataset_id=getenv("BQ_DATASET_ID", DEFAULT_DATASET),
        reports_db_path=_optional_str("RETAIL_AGENT_DB_PATH"),
        personas_dir=_optional_str("RETAIL_AGENT_PERSONAS_DIR"),
        max_bytes_billed=_int_env("BQ_MAX_BYTES_BILLED", DEFAULT_MAX_BYTES_BILLED),
        default_limit=_int_env("BQ_DEFAULT_LIMIT", DEFAULT_QUERY_LIMIT),
    )


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
