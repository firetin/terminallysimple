"""Tests for the atomic JSON helpers."""

from __future__ import annotations

import json
from pathlib import Path

from utils import storage


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "data.json"
    assert storage.save_json_atomic(target, {"a": 1}) is True
    assert storage.load_json(target) == {"a": 1}


def test_save_keeps_backup_of_previous_contents(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    storage.save_json_atomic(target, {"version": 1})
    storage.save_json_atomic(target, {"version": 2})

    assert storage.load_json(target) == {"version": 2}
    assert storage.load_json(target.with_name("data.json.bak")) == {"version": 1}


def test_save_leaves_no_temp_file_behind(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "data.json"
    storage.save_json_atomic(target, [1, 2, 3])
    assert sorted(p.name for p in target.parent.iterdir()) == ["data.json"]


def test_missing_file_returns_default(tmp_path: Path) -> None:
    assert storage.load_json(tmp_path / "nope.json", default={"x": 1}) == {"x": 1}


def test_corrupt_file_is_quarantined(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    target.write_text('{"broken": ')

    assert storage.load_json(target, default={}) == {}
    assert not target.exists()
    assert (tmp_path / "data.json.corrupt").exists()


def test_records_skip_only_the_bad_entry(tmp_path: Path) -> None:
    target = tmp_path / "records.json"
    target.write_text(json.dumps([{"text": "keep me"}, {"nope": True}, {"text": "me too"}]))

    records = storage.load_json_records(target, lambda item: item["text"])

    assert records == ["keep me", "me too"]


def test_records_reject_non_list_payload(tmp_path: Path) -> None:
    target = tmp_path / "records.json"
    target.write_text('{"not": "a list"}')
    assert storage.load_json_records(target, lambda item: item) == []


def test_migrate_file_only_when_target_missing(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy.json"
    target = tmp_path / "new" / "target.json"
    legacy.write_text('{"v": 1}')

    assert storage.migrate_file(legacy, target) is True
    assert storage.load_json(target) == {"v": 1}

    target.write_text('{"v": 2}')
    assert storage.migrate_file(legacy, target) is False
    assert storage.load_json(target) == {"v": 2}
