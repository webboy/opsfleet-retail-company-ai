"""Shared pytest fixtures."""

import pytest

from tests.helpers import make_settings


@pytest.fixture
def settings():
    return make_settings(default_limit=500)
