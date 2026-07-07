"""Shared pytest fixtures."""

from pathlib import Path

import pytest

from tests.helpers import make_settings


@pytest.fixture
def settings():
    return make_settings(default_limit=500)


@pytest.fixture(autouse=True)
def isolated_golden_bucket(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    bucket = tmp_path / "golden_bucket"
    bucket.mkdir()
    monkeypatch.setenv("GOLDEN_BUCKET_DIR", str(bucket))
    return bucket
