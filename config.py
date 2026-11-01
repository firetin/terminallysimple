"""
Configuration management for Terminally Simple.

The config file lives in the platform config directory (see
:mod:`utils.paths`) and is written atomically. Loading is lazy: importing this
module never touches the filesystem, which keeps tests isolated and startup
fast.
"""

from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import Any, Optional

from utils import paths, storage

logger = logging.getLogger(__name__)


class Config:
    """Manages application configuration and user preferences."""

    DEFAULT_CONFIG: dict[str, Any] = {
        "theme": "textual-dark",
        "weather_city": None,
        "weather_latitude": None,
        "weather_longitude": None,
        "weather_units": "celsius",
        "autosave_interval": 30.0,
    }

    def __init__(self, config_file: Optional[Path] = None) -> None:
        self._config_file = config_file
        self._config: Optional[dict[str, Any]] = None

    # ------------------------------------------------------------------ paths
    @property
    def config_file(self) -> Path:
        """Location of ``config.json`` (resolved lazily for testability)."""
        return self._config_file or paths.config_dir() / "config.json"

    @property
    def config_dir(self) -> Path:
        return self.config_file.parent

    # ------------------------------------------------------------------- load
    @property
    def data(self) -> dict[str, Any]:
        """The in-memory config, loaded on first access."""
        if self._config is None:
            self._config = self._load()
        return self._config

    def _load(self) -> dict[str, Any]:
        """Load configuration from disk, falling back to defaults."""
        storage.migrate_file(paths.legacy_config_dir() / "config.json", self.config_file)
        loaded = storage.load_json(self.config_file, default={})
        if not isinstance(loaded, dict):
            logger.warning("Config file %s is not an object; using defaults", self.config_file)
            loaded = {}
        return {**copy.deepcopy(self.DEFAULT_CONFIG), **loaded}

    # ------------------------------------------------------------------- save
    def save(self) -> bool:
        """Persist the current configuration to disk."""
        return storage.save_json_atomic(self.config_file, self.data)

    # ------------------------------------------------------------------ access
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value in memory (call :meth:`save` to persist)."""
        self.data[key] = value

    def update(self, values: dict[str, Any]) -> None:
        """Set several values at once."""
        self.data.update(values)

    def reset(self) -> None:
        """Reset configuration to defaults and persist."""
        self._config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.save()

    def reload(self) -> None:
        """Drop the in-memory copy so the next access re-reads the file."""
        self._config = None


# Global config instance. Cheap to create: nothing touches the disk until used.
config = Config()
