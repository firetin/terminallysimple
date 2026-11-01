"""File browser, new-document and validator behaviour."""

from __future__ import annotations

import pytest
from textual.widgets import TextArea

from app import TerminallySimple
from editor import EditorScreen, FileBrowser, FileItem
from utils import paths
from utils.validators import sanitize_filename


async def _open_editor(pilot) -> EditorScreen:
    await pilot.press("1")
    await pilot.pause()
    return pilot.app.screen


async def test_file_browser_opens_a_note() -> None:
    paths.ensure_dir(paths.notes_dir())
    (paths.notes_dir() / "a-note.md").write_text("from disk", encoding="utf-8")

    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        editor = await _open_editor(pilot)

        await pilot.press("ctrl+o")
        await pilot.pause()
        assert isinstance(app.screen, FileBrowser)

        app.screen.set_focus(app.screen.query_one(FileItem))
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, EditorScreen)
        assert editor.query_one(TextArea).text == "from disk"
        assert editor.current_file == paths.notes_dir() / "a-note.md"


async def test_file_browser_deletes_a_note_after_confirmation() -> None:
    paths.ensure_dir(paths.notes_dir())
    doomed = paths.notes_dir() / "doomed.md"
    doomed.write_text("bye", encoding="utf-8")

    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        await _open_editor(pilot)
        await pilot.press("ctrl+o")
        await pilot.pause()

        app.screen.set_focus(app.screen.query_one(FileItem))
        await pilot.press("ctrl+d")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()

        assert not doomed.exists()


async def test_new_document_clears_the_buffer() -> None:
    app = TerminallySimple()
    async with app.run_test(size=(100, 30)) as pilot:
        editor = await _open_editor(pilot)
        editor.query_one(TextArea).load_text("scratch")
        await pilot.pause()

        await pilot.press("ctrl+n")
        await pilot.pause()
        await pilot.press("y")  # confirm discarding
        await pilot.pause()

        assert editor.query_one(TextArea).text == ""
        assert editor.current_file is None


@pytest.mark.parametrize(
    "name",
    ["", "   ", "../escape", "sub/dir", "..", ".hidden", "bad:name", "CON", "con.txt"],
)
def test_sanitize_filename_rejects_dangerous_names(name: str) -> None:
    with pytest.raises(ValueError):
        sanitize_filename(name)


def test_sanitize_filename_accepts_normal_names() -> None:
    assert sanitize_filename("  my note.md  ") == "my note.md"
    assert sanitize_filename("notes-2026_11") == "notes-2026_11"


def test_sanitize_filename_limits_length() -> None:
    with pytest.raises(ValueError):
        sanitize_filename("x" * 400)
