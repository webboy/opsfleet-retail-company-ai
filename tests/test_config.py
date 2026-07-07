"""Tests for configuration loading."""

from os import getenv

from retail_agent.config import get_settings


def test_gcp_project_id_syncs_to_google_cloud_project(monkeypatch):
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.setenv("GCP_PROJECT_ID", "my-test-project")

    settings = get_settings(load_env=False)

    assert settings.gcp_project_id == "my-test-project"
    assert getenv("GOOGLE_CLOUD_PROJECT") == "my-test-project"
