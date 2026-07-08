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


def test_shell_env_overrides_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("RETAIL_AGENT_PERSONA=default\n", encoding="utf-8")
    monkeypatch.setenv("RETAIL_AGENT_PERSONA", "formal")

    def _load_tmp_env() -> None:
        from dotenv import load_dotenv

        load_dotenv(env_file, override=False)

    monkeypatch.setattr("retail_agent.config._load_env_file", _load_tmp_env)

    settings = get_settings(load_env=True)

    assert settings.persona == "formal"
