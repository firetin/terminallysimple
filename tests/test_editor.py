"""Behavioural tests for the editor (run through Textual's test driver)."""

from __future__ import annotations

from pathlib import Path

from textual.widgets import Input, TextArea

from app import TerminallySimple
from editor import ConfirmDialog, EditorScreen
from utils import paths


async def _open_editor(pilot) -> EditorScreen:
    await pilot.press("1")
    await pilot.pause()
    screen = pilot.app.screen
    assert isinstance(screen, EditorScreen)
    return screen


def _snapshot() -> Path:
    return paths.data_dir() / "autosave" / "untitled-autosave.md"


async def test_typed_text_is_persisted_when_the_app_quits() -> None:
    """Regression test: quitting used to throw away everything typed."""
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        editor = await _open_editor(pilot)
        editor.query_one(TextArea).load_text("hello world")
        await pilot.pause()
        assert editor.is_modified

    assert _snapshot().exists()
    assert _snapshot().read_text(encoding="utf-8") == "hello world"


async def test_quit_asks_before_dropping_unsaved_changes() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        editor = await _open_editor(pilot)
        editor.query_one(TextArea).load_text("draft")
        await pilot.pause()

        await pilot.press("ctrl+q")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmDialog)

        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, EditorScreen)
        assert editor.query_one(TextArea).text == "draft"


async def test_stale_snapshot_asks_before_recovering() -> None:
    _snapshot().parent.mkdir(parents=True, exist_ok=True)
    _snapshot().write_text("old draft", encoding="utf-8")

    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.press("1")
        await pilot.pause()

        assert isinstance(app.screen, ConfirmDialog)
        await pilot.press("y")
        await pilot.pause()

        assert isinstance(app.screen, EditorScreen)
        assert app.screen.query_one(TextArea).text == "old draft"


async def test_declining_recovery_discards_the_snapshot() -> None:
    _snapshot().parent.mkdir(parents=True, exist_ok=True)
    _snapshot().write_text("not wanted", encoding="utf-8")

    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.press("1")
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()

        assert not _snapshot().exists()
        assert app.screen.query_one(TextArea).text == ""


async def test_save_writes_into_the_documents_folder() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        editor = await _open_editor(pilot)
        editor.query_one(TextArea).load_text("note body")
        await pilot.pause()

        await pilot.press("ctrl+s")
        await pilot.pause()

        prompt_input = app.screen.query_one("#filename-input", Input)
        prompt_input.value = "my-note"
        await pilot.press("enter")
        await pilot.pause()

        saved = paths.notes_dir() / "my-note.md"
        assert saved.read_text(encoding="utf-8") == "note body"
        assert editor.current_file == saved
        assert editor.is_modified is False
        assert not _snapshot().exists()


def test_notes_are_not_stored_inside_the_package() -> None:
    editor = EditorScreen()
    package_root = Path(__file__).resolve().parent.parent

    assert package_root not in editor.documents_dir.resolve().parents


async def test_saving_over_an_existing_note_requires_confirmation() -> None:
    paths.ensure_dir(paths.notes_dir())
    existing = paths.notes_dir() / "precious.md"
    existing.write_text("PRECIOUS", encoding="utf-8")

    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        editor = await _open_editor(pilot)
        editor.query_one(TextArea).load_text("replacement")
        await pilot.pause()

        await pilot.press("ctrl+s")
        await pilot.pause()
        app.screen.query_one("#filename-input", Input).value = "precious"
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, ConfirmDialog)
        await pilot.press("n")
        await pilot.pause()
        assert existing.read_text(encoding="utf-8") == "PRECIOUS"

        await pilot.press("ctrl+s")
        await pilot.pause()
        app.screen.query_one("#filename-input", Input).value = "precious"
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()

        assert existing.read_text(encoding="utf-8") == "replacement"


async def test_rename_moves_the_file() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        editor = await _open_editor(pilot)
        editor.query_one(TextArea).load_text("content")
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()
        app.screen.query_one("#filename-input", Input).value = "first"
        await pilot.press("enter")
        await pilot.pause()

        await pilot.press("ctrl+r")
        await pilot.pause()
        app.screen.query_one("#rename-input", Input).value = "second"
        await pilot.press("enter")
        await pilot.pause()

        assert not (paths.notes_dir() / "first.md").exists()
        assert (paths.notes_dir() / "second.md").read_text(encoding="utf-8") == "content"
        assert editor.current_file == paths.notes_dir() / "second.md"
