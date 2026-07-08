"""Test helpers."""

from retail_agent.config import DEFAULT_EMBEDDING_MIN_SIMILARITY, DEFAULT_KEYWORD_MIN_OVERLAP, Settings


def make_settings(**overrides) -> Settings:
    defaults = {
        "gcp_project_id": "test-project",
        "google_api_key": "test-key",
        "model": "gemini-2.5-flash",
        "embedding_model": "gemini-embedding-001",
        "persona": "default",
        "provider": "gemini",
        "fallback_provider": None,
        "openrouter_api_key": None,
        "openrouter_model": "google/gemini-2.0-flash-exp:free",
        "ollama_host": "http://localhost:11434",
        "ollama_model": "llama3.2",
        "dataset_id": "bigquery-public-data.thelook_ecommerce",
        "reports_db_path": None,
        "personas_dir": None,
        "max_bytes_billed": 1_073_741_824,
        "default_limit": 1000,
        "mcp_max_response_rows": 100,
        "embedding_min_similarity": DEFAULT_EMBEDDING_MIN_SIMILARITY,
        "keyword_min_overlap": DEFAULT_KEYWORD_MIN_OVERLAP,
    }
    defaults.update(overrides)
    return Settings(**defaults)
