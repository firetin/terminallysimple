"""
Cross-platform application paths.

Uses ``platformdirs`` so the app follows each platform's conventions:
  * Linux/BSD: XDG (``~/.config/...``, ``~/.local/share/...``, ``~/Documents``)
  * macOS: ``~/Library/Application Support/...``
  * Windows: ``%APPDATA%`` / ``%LOCALAPPDATA%`` / ``Documents``

Directories are resolved lazily (not at import time) so tests can point
``XDG_CONFIG_HOME`` / ``XDG_DATA_HOME`` / ``HOME`` at a temporary directory.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from platformdirs import PlatformDirs

logger = logging.getLogger(__name__)

APP_NAME: str = "terminallysimple"
NOTES_FOLDER_NAME: str = "Terminally Simple"

#: Extensions the editor understands.
NOTE_EXTENSIONS: tuple[str, ...] = (".md", ".txt", ".text")


def _dirs() -> PlatformDirs:
    """Return a fresh ``PlatformDirs`` instance (re-reads environment)."""
    return PlatformDirs(appname=APP_NAME, appauthor=False, roaming=False)


def config_dir() -> Path:
    """Directory holding ``config.json``."""
    return Path(_dirs().user_config_dir)


def data_dir() -> Path:
    """Directory holding ``tasks.json``, the weather cache and autosave files."""
    return Path(_dirs().user_data_dir)


def notes_dir() -> Path:
    """Directory where the user's notes live."""
    return Path(_dirs().user_documents_dir) / NOTES_FOLDER_NAME


def log_file() -> Path:
    """Path of the application log file."""
    return data_dir() / "app.log"


def legacy_config_dir() -> Path:
    """Pre-``platformdirs`` location used by released versions."""
    return Path.home() / ".config" / APP_NAME


def ensure_dir(path: Path) -> Path:
    """Create ``path`` (and parents) if needed and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_app_dirs() -> None:
    """Create the config/data/notes directories the app writes to."""
    for path in (config_dir(), data_dir(), notes_dir()):
        try:
            ensure_dir(path)
        except OSError as e:  # pragma: no cover - depends on the environment
            logger.warning("Could not create directory %s: %s", path, e)


def legacy_notes_dir() -> Path:
    """Where pre-0.2 releases kept notes (inside the source/package tree)."""
    return Path(__file__).resolve().parent.parent / "notes"


def migrate_legacy_notes(target: Optional[Path] = None) -> int:
    """
    Copy notes from the old in-repo ``notes/`` folder into ``target``.

    Returns the number of files copied. Existing files are never overwritten.
    """
    source = legacy_notes_dir()
    destination = target or notes_dir()
    if not source.exists() or source.resolve() == destination.resolve():
        return 0

    copied = 0
    try:
        ensure_dir(destination)
    except OSError as e:
        logger.warning("Could not create %s: %s", destination, e)
        return 0

    for path in sorted(source.iterdir()):
        if not path.is_file() or path.suffix.lower() not in NOTE_EXTENSIONS:
            continue
        destination_file = destination / path.name
        if destination_file.exists():
            continue
        try:
            shutil.copy2(path, destination_file)
            copied += 1
        except OSError as e:
            logger.warning("Could not migrate note %s: %s", path, e)

    if copied:
        logger.info("Migrated %d note(s) from %s to %s", copied, source, destination)
    return copied
