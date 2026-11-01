"""Behavioural tests for the task manager screen."""

from __future__ import annotations

import json

from textual.widgets import Input

from app import TerminallySimple
from tasks import ConfirmDeleteDialog, TaskItem, TaskStorage


def _saved_tasks() -> list[dict]:
    return json.loads(TaskStorage().tasks_file.read_text(encoding="utf-8"))


async def _open_tasks(pilot) -> None:
    await pilot.press("2")
    await pilot.pause()


async def _add_task(pilot, text: str) -> None:
    await pilot.press("a")
    await pilot.pause()
    pilot.app.screen.query_one("#task-input-field", Input).value = text
    await pilot.press("enter")
    await pilot.pause()


async def test_add_task_persists_immediately() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await _open_tasks(pilot)
        await _add_task(pilot, "buy milk")

        assert [t["text"] for t in _saved_tasks()] == ["buy milk"]
        assert len(app.screen.query(TaskItem)) == 1


async def test_toggle_task_persists() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await _open_tasks(pilot)
        await _add_task(pilot, "write tests")

        await pilot.press("space")
        await pilot.pause()

        assert _saved_tasks()[0]["completed"] is True


async def test_delete_task_asks_for_confirmation() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await _open_tasks(pilot)
        await _add_task(pilot, "temporary")

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmDeleteDialog)

        await pilot.press("n")
        await pilot.pause()
        assert _saved_tasks() != []

        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert _saved_tasks() == []


async def test_clear_completed_tasks() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await _open_tasks(pilot)
        await _add_task(pilot, "done")
        await _add_task(pilot, "pending")

        await pilot.press("down")
        await pilot.pause()
        await pilot.press("space")  # complete the first task again
        await pilot.pause()

        await pilot.press("c")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()

        texts = [t["text"] for t in _saved_tasks()]
        assert len(texts) <= 2
        assert all(not t["completed"] for t in _saved_tasks())
