"""Shared pytest fixtures.

Every test runs against a throw-away HOME / XDG tree so nothing touches the
developer's real config, notes or task list.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point every user directory at ``tmp_path`` for the duration of a test."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.chdir(tmp_path)

    # The global Config caches its contents; drop that cache between tests.
    from config import config as global_config

    global_config.reload()
    yield tmp_path
    global_config.reload()
