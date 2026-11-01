"""Tests for task model and persistence."""

from __future__ import annotations

import json
from pathlib import Path

from tasks import Task, TaskStorage


def test_task_roundtrip() -> None:
    task = Task("write tests", completed=True, task_id=7)
    restored = Task.from_dict(task.to_dict())

    assert (restored.id, restored.text, restored.completed) == (7, "write tests", True)
    assert restored.created_at == task.created_at


def test_task_from_dict_without_id_is_tolerated() -> None:
    task = Task.from_dict({"text": "legacy"})
    assert task.text == "legacy"
    assert isinstance(task.id, int)
    assert task.completed is False


def test_storage_roundtrip(tmp_path: Path) -> None:
    store = TaskStorage(tmp_path / "tasks.json")
    assert store.load_tasks() == []

    store.save_tasks([Task("one", task_id=1), Task("two", task_id=2, completed=True)])
    loaded = store.load_tasks()

    assert [t.text for t in loaded] == ["one", "two"]
    assert loaded[1].completed is True


def test_storage_keeps_good_records_when_one_is_broken(tmp_path: Path) -> None:
    target = tmp_path / "tasks.json"
    target.write_text(
        json.dumps(
            [
                {"id": 1, "text": "good", "completed": False, "created_at": "2026-01-01T10:00:00"},
                {"id": 2, "completed": False},
                {"id": 3, "text": "also good", "completed": True, "created_at": "2026-01-02T10:00:00"},
            ]
        )
    )

    loaded = TaskStorage(target).load_tasks()

    assert [t.text for t in loaded] == ["good", "also good"]


def test_storage_survives_truncated_file(tmp_path: Path) -> None:
    target = tmp_path / "tasks.json"
    target.write_text('[{"id": 1, "text": "half writ')

    assert TaskStorage(target).load_tasks() == []
    assert (tmp_path / "tasks.json.corrupt").exists()


def test_storage_writes_backup(tmp_path: Path) -> None:
    store = TaskStorage(tmp_path / "tasks.json")
    store.save_tasks([Task("one", task_id=1)])
    store.save_tasks([Task("one", task_id=1), Task("two", task_id=2)])

    previous = json.loads((tmp_path / "tasks.json.bak").read_text())
    assert len(previous) == 1
