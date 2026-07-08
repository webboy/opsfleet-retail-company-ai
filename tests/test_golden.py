"""Tests for Golden Bucket trio store."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retail_agent.golden import (
    FakeEmbedder,
    TrioStore,
    format_trios_for_prompt,
    load_trio_file,
    load_trios,
)
from tests.helpers import make_settings


SAMPLE_TRIO = """\
---
id: sample-trio
question: Who are our top customers by total spend?
tags:
  - customers
  - revenue
sql: |
  SELECT user_id, SUM(sale_price) AS total_spend
  FROM `bigquery-public-data.thelook_ecommerce.order_items`
  GROUP BY user_id
  LIMIT 10
report: |
  Rank customers by completed order spend.
---
"""


OTHER_TRIO = """\
---
id: monthly-revenue
question: What was monthly revenue last year?
tags:
  - revenue
  - monthly
sql: |
  SELECT month, SUM(sale_price) AS revenue
  FROM `bigquery-public-data.thelook_ecommerce.orders`
  GROUP BY month
report: |
  Monthly revenue trend.
---
"""


@pytest.fixture
def bucket_dir(tmp_path: Path) -> Path:
    (tmp_path / "sample.md").write_text(SAMPLE_TRIO, encoding="utf-8")
    (tmp_path / "monthly.md").write_text(OTHER_TRIO, encoding="utf-8")
    return tmp_path


def test_load_trio_file_parses_front_matter(bucket_dir: Path):
    trio = load_trio_file(bucket_dir / "sample.md")

    assert trio.id == "sample-trio"
    assert "top customers" in trio.question.lower()
    assert "order_items" in trio.sql
    assert "completed order spend" in trio.report
    assert trio.tags == ("customers", "revenue")


def test_load_trios_from_directory(bucket_dir: Path):
    trios = load_trios(bucket_dir)

    assert len(trios) == 2
    assert {trio.id for trio in trios} == {"sample-trio", "monthly-revenue"}


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("broken-missing-id.md", "---\nquestion: broken\nsql: SELECT 1\n---\nbody\n"),
        ("broken-yaml.md", "---\nquestion: [unclosed\nsql: SELECT 1\nid: broken\n---\nbody\n"),
        ("broken-no-frontmatter.md", "Just a markdown body without front matter.\n"),
    ],
)
def test_load_trios_skips_malformed_files(bucket_dir: Path, filename: str, content: str, caplog):
    (bucket_dir / filename).write_text(content, encoding="utf-8")

    with caplog.at_level("WARNING"):
        trios = load_trios(bucket_dir)

    assert len(trios) == 2
    assert {trio.id for trio in trios} == {"sample-trio", "monthly-revenue"}
    assert any(filename in record.message for record in caplog.records)
    assert any("Skipping invalid trio file" in record.message for record in caplog.records)


def test_trio_store_starts_with_malformed_file_present(bucket_dir: Path, caplog):
    (bucket_dir / "zz-broken.md").write_text(
        "---\nquestion: broken\nsql: SELECT 1\n---\nbody\n",
        encoding="utf-8",
    )

    with caplog.at_level("WARNING"):
        store = TrioStore(
            bucket_dir,
            embedder=FakeEmbedder(),
            settings=make_settings(),
            embedding_enabled=True,
            top_k=1,
        )

    result = store.retrieve("Who are the top customers by spend?")

    assert result.trios[0].id == "sample-trio"
    assert any("zz-broken.md" in record.message for record in caplog.records)


def test_fake_embedding_ranks_similar_question(bucket_dir: Path):
    store = TrioStore(
        bucket_dir,
        embedder=FakeEmbedder(),
        settings=make_settings(),
        embedding_enabled=True,
        top_k=1,
    )

    result = store.retrieve("Who are the top customers by spend?")

    assert result.method == "embedding"
    assert len(result.trios) == 1
    assert result.trios[0].id == "sample-trio"


def test_embedding_failure_falls_back_to_keyword(bucket_dir: Path):
    class BrokenEmbedder:
        def embed_query(self, text: str) -> list[float]:
            raise RuntimeError("embedding unavailable")

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            raise RuntimeError("embedding unavailable")

    store = TrioStore(
        bucket_dir,
        embedder=BrokenEmbedder(),
        settings=make_settings(),
        embedding_enabled=True,
        top_k=1,
    )

    result = store.retrieve("monthly revenue last year")

    assert result.method == "keyword"
    assert result.trios[0].id == "monthly-revenue"


def test_capture_candidate_writes_jsonl(bucket_dir: Path):
    store = TrioStore(
        bucket_dir,
        embedder=FakeEmbedder(),
        settings=make_settings(),
        embedding_enabled=False,
    )

    path = store.capture_candidate(
        question="Who are our top customers?",
        sql="SELECT 1",
        report="Top customers summary",
        retrieved_trio_ids=["sample-trio"],
        user_id="alice",
    )

    assert path.exists()
    record = json.loads(path.read_text(encoding="utf-8").strip())
    assert record["question"] == "Who are our top customers?"
    assert record["sql"] == "SELECT 1"
    assert record["report"] == "Top customers summary"
    assert record["retrieved_trio_ids"] == ["sample-trio"]
    assert record["user_id"] == "alice"
    assert "timestamp" in record


def test_format_trios_for_prompt_includes_examples(bucket_dir: Path):
    trios = load_trios(bucket_dir)
    sample = next(trio for trio in trios if trio.id == "sample-trio")
    prompt = format_trios_for_prompt([sample])

    assert "Example 1:" in prompt
    assert "top customers by total spend" in prompt.lower()
    assert "SELECT user_id" in prompt
