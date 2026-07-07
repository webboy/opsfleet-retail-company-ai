"""Load static schema documentation for prompts."""

from functools import lru_cache
from importlib import resources


@lru_cache(maxsize=1)
def load_schema_doc() -> str:
    return resources.files("retail_agent.assets").joinpath("schema.md").read_text(
        encoding="utf-8"
    )
