"""
Safe JSON persistence.

Every write goes through :func:`save_json_atomic` (temp file + ``os.replace``)
and keeps a ``.bak`` copy of the previous contents, so a crash or a full disk
can never leave a half-written file behind. Reads are tolerant: a corrupt file
returns the default value instead of raising, and a corrupt *record* inside a
list is skipped instead of discarding the whole list.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

#: File that receives the previous contents on every successful save.
BACKUP_SUFFIX: str = ".bak"


def _fsync_directory(path: Path) -> None:  # pragma: no cover - platform dependent
    """Best-effort fsync of the directory entry so the rename is durable."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def load_json(path: Path, default: Any = None) -> Any:
    """
    Load JSON from ``path``.

    Returns ``default`` when the file is missing, unreadable or corrupt.
    A corrupt file is renamed to ``<name>.corrupt`` so the data can be
    recovered manually instead of being silently overwritten.
    """
    if not path.exists():
        return default

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Corrupt JSON in %s (%s); keeping a copy", path, e)
        _quarantine(path)
        return default
    except OSError as e:
        logger.error("Could not read %s: %s", path, e)
        return default


def load_json_records(
    path: Path,
    factory: Callable[[Any], T],
) -> list[T]:
    """
    Load a list of records, skipping (and reporting) individual bad entries.

    A single malformed record must never discard the rest of the user's data.
    """
    raw = load_json(path, default=[])
    if not isinstance(raw, list):
        logger.error("%s does not contain a list; ignoring", path)
        return []

    records: list[T] = []
    skipped = 0
    for index, item in enumerate(raw):
        try:
            records.append(factory(item))
        except (KeyError, TypeError, ValueError) as e:
            skipped += 1
            logger.warning("Skipping malformed record #%d in %s: %s", index, path, e)

    if skipped:
        logger.error(
            "%d of %d records in %s could not be read and were skipped",
            skipped,
            len(raw),
            path,
        )
    return records


def save_json_atomic(path: Path, data: Any) -> bool:
    """
    Atomically write ``data`` as JSON to ``path``.

    Returns ``True`` on success. The previous contents are preserved as
    ``<name>.bak``.
    """
    path = Path(path)
    tmp_path = path.with_name(path.name + ".tmp")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        if path.exists():
            try:
                shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
            except OSError as e:  # pragma: no cover - unlikely
                logger.warning("Could not write backup for %s: %s", path, e)

        os.replace(tmp_path, path)
        _fsync_directory(path.parent)
        return True

    except (OSError, TypeError, ValueError) as e:
        logger.error("Could not save %s: %s", path, e)
        with contextlib.suppress(OSError):
            tmp_path.unlink(missing_ok=True)
        return False


def _quarantine(path: Path) -> None:
    """Move a corrupt file aside so the next save does not destroy it."""
    target = path.with_name(path.name + ".corrupt")
    try:
        shutil.move(str(path), str(target))
        logger.warning("Moved corrupt file %s to %s", path, target)
    except OSError as e:  # pragma: no cover
        logger.warning("Could not quarantine %s: %s", path, e)


def write_text_atomic(path: Path, text: str) -> bool:
    """
    Atomically write ``text`` to ``path`` (temp file + ``os.replace``).

    Used for notes and autosave snapshots so a crash mid-write cannot truncate
    the user's document.
    """
    path = Path(path)
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
        return True
    except OSError as e:
        logger.error("Could not write %s: %s", path, e)
        with contextlib.suppress(OSError):
            tmp_path.unlink(missing_ok=True)
        return False


def read_text(path: Path, default: str = "") -> str:
    """Read text from ``path``, returning ``default`` when unreadable."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default
    except (OSError, UnicodeDecodeError) as e:
        logger.error("Could not read %s: %s", path, e)
        return default


def migrate_file(legacy: Path, target: Path) -> bool:
    """
    Copy ``legacy`` to ``target`` when ``target`` does not exist yet.

    Used to move data written by older releases into the platform directory.
    Returns ``True`` when a migration happened.
    """
    if target.exists() or not legacy.exists() or legacy == target:
        return False
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy, target)
        logger.info("Migrated %s -> %s", legacy, target)
        return True
    except OSError as e:
        logger.warning("Could not migrate %s: %s", legacy, e)
        return False
