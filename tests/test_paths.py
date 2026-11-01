"""Tests for cross-platform paths and legacy migration."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from utils import paths


def test_directories_follow_the_environment(isolated_home: Path) -> None:
    assert paths.config_dir() == isolated_home / "config" / "terminallysimple"
    assert paths.data_dir() == isolated_home / "data" / "terminallysimple"
    assert paths.notes_dir().parent == isolated_home / "home" / "Documents"


def test_ensure_app_dirs_creates_everything() -> None:
    paths.ensure_app_dirs()

    assert paths.config_dir().is_dir()
    assert paths.data_dir().is_dir()
    assert paths.notes_dir().is_dir()


def test_legacy_notes_are_migrated(tmp_path: Path) -> None:
    legacy = paths.legacy_notes_dir()
    created_legacy = False
    if not legacy.exists():
        legacy.mkdir(parents=True)
        created_legacy = True

    note = legacy / "migrated-note.md"
    note.write_text("from the old folder", encoding="utf-8")
    target = tmp_path / "documents"

    try:
        copied = paths.migrate_legacy_notes(target)
        assert copied >= 1
        assert (target / "migrated-note.md").read_text(encoding="utf-8") == "from the old folder"

        # Second run must not overwrite an existing file.
        (target / "migrated-note.md").write_text("edited", encoding="utf-8")
        paths.migrate_legacy_notes(target)
        assert (target / "migrated-note.md").read_text(encoding="utf-8") == "edited"
    finally:
        note.unlink(missing_ok=True)
        if created_legacy:
            legacy.rmdir()


@pytest.mark.skipif(os.name == "nt", reason="POSIX permissions only")
def test_editor_survives_a_read_only_notes_folder(tmp_path: Path) -> None:
    """A read-only notes folder must not prevent the editor from opening."""
    readonly = tmp_path / "readonly"
    readonly.mkdir()
    readonly.chmod(0o500)

    from config import config
    from editor import EditorScreen

    config.set("notes_dir", str(readonly))
    try:
        screen = EditorScreen()  # must not raise
        assert screen.documents_dir == readonly
    finally:
        config.set("notes_dir", None)
        readonly.chmod(0o700)
