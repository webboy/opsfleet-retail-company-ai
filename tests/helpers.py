"""Test helpers."""

from retail_agent.config import Settings


def make_settings(**overrides) -> Settings:
    defaults = {
        "gcp_project_id": "test-project",
        "google_api_key": None,
        "model": "gemini-2.5-flash",
        "persona": "default",
        "dataset_id": "bigquery-public-data.thelook_ecommerce",
        "max_bytes_billed": 1_073_741_824,
        "default_limit": 1000,
    }
    defaults.update(overrides)
    return Settings(**defaults)
