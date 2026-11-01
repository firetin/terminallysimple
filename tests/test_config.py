"""Tests for the configuration layer."""

from __future__ import annotations

import json
from pathlib import Path

from config import Config
from utils import paths


def test_defaults_when_file_missing() -> None:
    cfg = Config()
    assert cfg.get("theme") == "textual-dark"
    assert cfg.get("weather_city") is None
    assert cfg.config_file == paths.config_dir() / "config.json"


def test_import_does_not_create_directories() -> None:
    assert not paths.config_dir().exists()


def test_set_save_roundtrip() -> None:
    cfg = Config()
    cfg.set("theme", "nord")
    assert cfg.save() is True

    assert Config().get("theme") == "nord"
    assert json.loads(cfg.config_file.read_text())["theme"] == "nord"


def test_corrupt_config_falls_back_to_defaults() -> None:
    cfg = Config()
    cfg.config_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.config_file.write_text("{not json")

    assert cfg.get("theme") == "textual-dark"
    assert cfg.config_file.with_name("config.json.corrupt").exists()


def test_reset_restores_defaults() -> None:
    cfg = Config()
    cfg.set("theme", "dracula")
    cfg.save()

    cfg.reset()

    assert cfg.get("theme") == "textual-dark"
    assert Config().get("theme") == "textual-dark"


def test_unknown_keys_are_preserved() -> None:
    cfg = Config()
    cfg.config_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.config_file.write_text(json.dumps({"theme": "nord", "future_option": True}))
    cfg.reload()

    assert cfg.get("future_option") is True
    assert cfg.get("theme") == "nord"
